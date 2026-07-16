from vna import VNA
from controller import Controller
from datetime import datetime
import numpy as np
import time

#%%
# ANECHOIC CHAMBER

class AnechoicChamber:

    def __init__(self,
                 start_freq,
                 stop_freq,
                 freq_resolution,
                 IF_bandwidth,
                 average_mode:str,
                 average_count=None
                 ):
        
        self.vna = VNA(start_freq, stop_freq, freq_resolution, IF_bandwidth)
        self.vna.set_average(average_mode, average_count)
        print("--- VNA IS SET! ---\n")
        
        self.ctrl = Controller()
        self.ctrl.rel_to_abs()
        print("--- MOTORS ARE SET! ---\n")
        
        
#%%
### MEASURE ###################################################################
      
    ### perform a sweep ### 
    def sweep(self, folder:str, measure_name:str, position:list):
        
        self.ctrl.go_to(position)
        self.ctrl.read_position(print_pos=True)   #reach position
        
        print("Measuring...")
        self.vna.single_sweep()   #measure one sweep
        
        file_name = self.generate_file_name(measure_name)
        #file_name = self.old_file_name()                   # <-- TEMPORARY!!
        self.vna.save_data_on_vna(file_name, folder)   #save sweep data
        
        self.log_sweep(file_name)
        
        print("...saved!\n\n")
        
    
    ### generate file name for each sweep ###
    def generate_file_name(self, measure_name:str):
        name = str(measure_name)
        for n, mot in zip(self.ctrl.mot_axis, self.ctrl.motor.values()):
            name += f"_ax{n}_{mot.read_position()}"   #specify motors position
        return name
    
    def old_file_name(self):
        return self.ctrl.motor[1].read_position()   # <-- TEMPORARY!!
    
    
    ### generate folder for the whole scan ###
    def folder_name_VNA(self, count:int, path:str, measure_name:str):   #create name with date and measure count
        if path[-1]!="/":
            path+="/"
        return f"{path}{datetime.now().strftime('%Y_%m_%d')}_{measure_name}_{count:03d}"
    
    def make_measure_folder(self, path:str, measure_name:str):   #create folder on VNA
        if path[-1]!="/":
            path+="/"
        self.vna.make_path(path)   #create desired path inside "D:/_ANECHOIC_CHAMBER_/"
        count = 0
        while True:
            folder = self.folder_name_VNA(count, path, measure_name)
            full_path = f"D:/_ANECHOIC_CHAMBER_/{folder}"
            if self.vna.find_folder(full_path) == 1:   #add numbering for repeated measures
                count +=1
            elif self.vna.find_folder(full_path) == 0:
                self.vna.make_path(folder)
                return folder
            
            
#%%
### LOG FILE ##################################################################
    
    ### write a header with useful information for the log file ###
    def log_write_header(self, folder:str, measure_name:str):
        self.log_path = f"D:/_ANECHOIC_CHAMBER_/{folder}/log_scan.txt"
        now = datetime.now()
        
        lines = []
        
        lines.append(f"Date: {now.strftime('%Y-%m-%d')}")   #measurement info
        lines.append(f"Start time: {now.strftime('%H:%M:%S')}")
        lines.append(f"Measurement name: {measure_name}\n")
        
        # at some point add alignment positions here <--
        
        lines.append("--- VNA setup ---")   #VNA info
        lines.append(f"Start frequency (Hz): {self.vna.start_freq}")
        lines.append(f"Stop frequency (Hz): {self.vna.stop_freq}")
        lines.append(f"Frequency resolution (Hz): {self.vna.freq_resolution}")
        lines.append(f"IF bandwidth (Hz): {self.vna.IF_bandwidth}")
        lines.append(f"Average mode: {self.vna.read_average_mode()}")
        lines.append(f"Average count: {self.vna.read_average_count()}\n")
        
        lines.append("--- Motors ---")   #motors info
        for n, mot in zip(self.ctrl.mot_axis, self.ctrl.motor.values()):
            lines.append(f"Axis {n}: {mot.motor_name()}")
            
        self.log_buffer = "\n".join(lines) + "\n\n"
        self.vna.write_file_on_vna(self.log_path, self.log_buffer)


    ### add a line in the log for each sweep, with file name and actual motor position ###
    def log_sweep(self, file_name:str):
        
        positions = str(self.ctrl.read_position())
        
        self.log_buffer += f"{file_name}\t{positions}\n"
        self.vna.write_file_on_vna(self.log_path, self.log_buffer)
        
    
    ### write the ending line of the log file, for successful scans ###
    def log_write_end(self):
        now = datetime.now()
        
        lines = []
        
        lines.append("\n----------------------------------")
        lines.append("--- SCAN COMPLETED SUCCESFULLY ---")
        lines.append("----------------------------------\n")
        
        lines.append(f"End time: {now.strftime('%H:%M:%S')}")
        
        log_end = "\n".join(lines)
        
        self.log_buffer += log_end
        self.vna.write_file_on_vna(self.log_path, self.log_buffer)


#%%
### SCAN ######################################################################

    ### generate the whole list of positions to measure during a single scan ###
    def generate_positions(self, *intervals):
        """
        *intervals : scalar or tuple of [start, stop, step]
        
        Each interval defines the range of movement of each motor, following
        the axis order.
        - If a tuple [start, stop, step] is provided, the positions will
          span from start to stop (inclusive) with the given step size.
        - If a scalar is provided, the position is fixed at that value.
        """
        if len(intervals) != len(self.ctrl.mot_axis):
            raise ValueError(f"Expected {len(self.ctrl.mot_axis)} intervals, but {len(intervals)} were provided")
            
        arrays = []
        for item in intervals:
            
            if np.isscalar(item):   #if a scalar it's provided the position is fixed
                arrays.append(np.array([item]))
                
            else:   #if an interval is provided all the different positions are computed
                start, stop, step = item
                num = round((stop - start) / step) + 1
                arrays.append(np.linspace(start, stop, num))
                
        grids = np.meshgrid(*arrays, indexing='ij')
        positions = np.stack([g.ravel() for g in grids], axis=-1)   #list of all the combinations
        print(f"{len(positions)} different poses were generated\n")
        return positions

    
    ### perform a scan ###             
    def scan(self, path:str, measure_name:str, positions:list):
        start_time = time.time()
        
        self.vna.hold_sweep()   #stop VNA measure
        
        folder = self.make_measure_folder(path, measure_name)
        
        self.log_write_header(folder, measure_name)   #initialize log file
        
        for pos in positions:
            self.sweep(folder, measure_name, pos)   #perform measurement in each position
            
        self.ctrl.go_home()
        self.ctrl.read_position(print_pos=True)   #go back to the zero position
        
        end_time = time.time()
        
        self.vna.continuous_sweep()   #restore VNA continuous sweep mode
        
        self.log_write_end()   #end log file
        
        print("\n----------------------")
        print("--- SCAN COMPLETED ---")
        print("----------------------\n")
        print(f"The scan took {end_time - start_time} s")
        
    