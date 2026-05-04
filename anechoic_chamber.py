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
### SCAN ######################################################################

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
    

    def sweep(self, folder:str, measure_name:str, position:list):
        
        self.ctrl.go_to(position)
        self.ctrl.read_position(print_pos=True)   #reach position
        
        print("Measuring...")
        self.vna.single_sweep()   #measure one sweep
        
        #file_name = self.generate_file_name(measure_name)
        file_name = self.old_file_name()                   # <-- TEMPORARY!!
        self.vna.save_data_on_vna(file_name, folder)   #save sweep data
        print("...saved!\n\n")
        
        
    def generate_file_name(self, measure_name:str):
        name = str(measure_name)
        for n, mot in zip(self.ctrl.mot_axis, self.ctrl.motor.values()):
            name += f"_ax{n}_{mot.read_position()}"
        return name
    
    
    def old_file_name(self):
        return self.ctrl.motor[1].read_position()   # <-- TEMPORARY!!
    
    
    def folder_name_VNA(self, count:int, band:str, measure_name:str):
        path = f"{band}/{measure_name}/"
        name = f"{measure_name}"
        return f"{path}{datetime.now().strftime('%Y_%m_%d')}_{name}_{count:03d}"
    
    
    def make_VNA_folder(self, band:str, measure_name:str):
        self.vna.send_message(f"MMEM:MDIR 'D:/_ANECHOIC_CHAMBER_/{band}/{measure_name}'\r")
        count = 0
        while True:
            folder = self.folder_name_VNA(count, band, measure_name)
            path = f"D:/_ANECHOIC_CHAMBER_/{folder}"
            if self.vna.find_folder(path) == 1:
                count +=1
            elif self.vna.find_folder(path) == 0:
                self.vna.send_message(f"MMEM:MDIR '{path}'\r")
                return folder
                
    
 
    def scan(self, band:str, measure_name:str, positions:list):
        start_time = time.time()
        
        self.vna.hold_sweep()   #stop VNA measure
        
        folder = self.make_VNA_folder(band, measure_name)
        
        for pos in positions:
            self.sweep(folder, measure_name, pos)   #perform measurement in each position
            
        self.ctrl.go_home()
        self.ctrl.read_position(print_pos=True)   #go back to the zero position
        
        end_time = time.time()
        
        self.vna.continuous_sweep()   #restore VNA continuous sweep mode
        
        print("\n----------------------")
        print("--- SCAN COMPLETED ---")
        print("----------------------\n")
        print(f"The scan took {end_time - start_time} s")
        
    