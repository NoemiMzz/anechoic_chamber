import time
import socket

#ip_addr = "169.254.217.24"
#port = 5024


#%%
class VNA:
    def __init__(self,
                 start_freq,
                 stop_freq,
                 freq_resolution,
                 IF_bandwidth,
                 ip_addr="169.254.217.24",
                 port=5024
                 ):
        
        self.start_freq = start_freq
        self.stop_freq = stop_freq
        self.freq_resolution = freq_resolution
        self.IF_bandwidth = IF_bandwidth
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port))
        print("Connected to VNA socket!\n")
        
        self.set_bandwidth(start_freq, stop_freq) #GHz
        print(f"Bandwidth: {self.read_start_freq()} - {self.read_stop_freq()} GHz")
        
        self.set_IF_bandwidth(IF_bandwidth) #Hz
        print(f"IF bandwidht: {self.read_IF_bandwidth()} Hz\n")
        
        self.set_freq_points(start_freq, stop_freq, freq_resolution)
        
        self.point_sweep_OFF()
        
        self.standard_windows_setup()



###############################################################################

    ### send a command to the VNA ###
    def send_message(self, message, return_answerback=False):
        self.socket.send(message.encode())
        time.sleep(0.2)
        answerback = self.socket.recv(1024)
        if return_answerback:
            return answerback.decode(errors="ignore")
    
    
    ### interpret VNA responses ###
    def read_answer(self, answer):
        value = answer.strip().splitlines()[1]
        return value
        
        
        
### FREQUENCY #################################################################
    
    ### set start and stop frequency for different bands ###
    def set_start_freq(self, start_freq):
        self.send_message(f"SENS:FREQ:STAR {start_freq * 10**9}\r") #GHz
        
    def set_stop_freq(self, stop_freq):
        self.send_message(f"SENS:FREQ:STOP {stop_freq * 10**9}\r") #GHz
    
    def set_bandwidth(self, start_freq, stop_freq):
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
    
    ### set IF bandwidth ###
    def set_IF_bandwidth(self, IF_bandwidth):
        self.send_message(f"SENS:BWID {str(IF_bandwidth)} HZ\r") #Hz
    
    ### set the number of frequency points per sweep ###
    def set_freq_points(self, start_freq, stop_freq, freq_resolution):
        points = round((stop_freq - start_freq) / freq_resolution) + 1
        self.send_message(f"SENS:SWE:POIN {points}\r")
        
        
    ### read start and stop frequency ###
    def read_start_freq(self, print_freq=False):
        answer = self.send_message("SENS:FREQ:STAR?\r", return_answerback=True)
        sf = float(self.read_answer(answer)) / 10**9   #GHz
        if print_freq:
            print(f"Start frequency: {sf} GHz")
        return sf
    
    def read_stop_freq(self, print_freq=False):
        answer = self.send_message("SENS:FREQ:STOP?\r", return_answerback=True)
        sf = float(self.read_answer(answer)) / 10**9   #GHz
        if print_freq:
            print(f"Stop frequency: {sf} GHz")
        return sf
    
    ### read IF bandwidth ###
    def read_IF_bandwidth(self, print_freq=False):
        answer = self.send_message("SENS:BWID?\r", return_answerback=True)
        f = float(self.read_answer(answer))   #Hz
        if print_freq:
            print(f"IF bandwidth: {f} Hz")
        return f
        
        
        
### AVERAGE ###################################################################
    
    ### switch on/off averaging ###
    def average_ON(self):
        self.send_message("SENS:AVER ON\r")
        
    def average_OFF(self):
        self.send_message("SENS:AVER OFF\r")
    
    ### set average mode to: point ###
    def set_point_average(self):
        self.send_message("SENS:AVER:MODE POIN\r")
        
    ### set average mode to: sweep ###
    def set_sweep_average(self):
        self.send_message("SENS:AVER:MODE SWEEP\r")
    
    ### number of points/sweeps to average on ###
    def set_average_count(self, count:int):
        self.send_message(f"SENS:AVER:COUN {count}\r")
        
    
    ### read wether average is on/off ###
    def read_average_status(self):
        answer = self.send_message("SENS:AVER:STAT?\r", return_answerback=True)
        value = int(self.read_answer(answer))
        if value == 1:
            return 'ON'
        elif value == 0:
            return 'OFF'
    
    ### read the average mode ###
    def read_average_mode(self):
        answer = self.send_message("SENS:AVER:MODE?\r", return_answerback=True)
        value = self.read_answer(answer)
        if value == 'POIN':
            return 'point'
        elif value == 'SWE':
            return 'sweep'
        
    ### read the number of points/sweeps to average on ###
    def read_average_count(self):
        answer = self.send_message("SENS:AVER:COUN?\r", return_answerback=True)
        value = self.read_answer(answer)
        return int(value)
    
    
    ### summary average function ###
    def set_average(self, mode: str, count=None):
        valid_modes = {'OFF', 'point', 'sweep'}
    
        if mode not in valid_modes:
            raise ValueError(f"Argument 'mode' must be one of {valid_modes} (received '{mode}')")
    
        if mode == 'OFF':
            self.average_OFF()
            print(f"Averaging is {self.read_average_status()}\n")
            return

        if count is None:
            raise ValueError(f"'count' is required when mode is '{mode}'")
    
        self.average_ON()
    
        if mode == 'point':
            self.set_point_average()
        elif mode == 'sweep':
            self.set_sweep_average()
    
        self.set_average_count(count)
        print(f"Averaging on {self.read_average_count()} {self.read_average_mode()}s\n")
        
        
        
### SWEEP #####################################################################

    ### switch on/off point sweep ###
    def point_sweep_ON(self):
        self.send_message("SENS:SWE:GEN:POIN 1\r")
        
    def point_sweep_OFF(self):
        self.send_message("SENS:SWE:GEN:POIN 0\r")
     
        
    ### hold sweep ###
    def hold_sweep(self):
        self.send_message("SENS:SWE:MODE HOLD\r")
    
    ### make a single sweep ###
    def single_sweep(self):
        self.send_message("SENS:SWE:MODE SING\r")
        while True:
            if self.read_sweep_mode() == 'HOLD':   #waits for the sweep to be performed
                break
            time.sleep(0.2)
        
    ### sweep continuously ###
    def continuous_sweep(self):
        self.send_message("SENS:SWE:MODE CONT\r")
        
    
    ### read sweep mode ###
    def read_sweep_mode(self):
        answer = self.send_message("SENS:SWE:MODE?\r", return_answerback=True)
        value = self.read_answer(answer)
        return value
        
    
    
### DISPLAY ###################################################################
       
    ### delete all traces/windows ###
    def delete_all_traces(self):
        self.send_message("CALC:PAR:DEL:ALL\r")
        
    def delete_all_windows(self, max_windows:int = 16):
        for window_number in range(1, max_windows + 1):
            self.send_message(f"DISP:WIND{window_number}:STAT OFF\r")
    
    ### create a new trace/window ###
    def add_new_trace(self, channel:int, trace_name:str, s_parameter:str, window_number:int, trace_slot:int):
        """
        Defines a new trace on the specified channel and assigns it to a display window.
        Args:
            channel:        Channel number on which the trace is created (e.g., 1)
            trace_name:     User-defined string identifier for the trace (e.g., "S21_trace")
            s_parameter:    S-parameter to measure (e.g., "S11", "S21", "S12", "S22")
            window_number:  Window in which the trace will be displayed (e.g., 1)
            trace_slot:     Display slot index within the window (e.g., 1, 2, 3...)
        """
        self.send_message(f"CALC{channel}:PAR:DEF:EXT '{trace_name}','{s_parameter}'\r")
        self.send_message(f"DISP:WIND{window_number}:TRAC{trace_slot}:FEED '{trace_name}'\r")
            
    def create_new_window(self, window_number:int):
        self.send_message(f"DISP:WIND{window_number}:STAT ON\r")
    
    
    ### display all the S-parameters, one per window ###
    def standard_windows_setup(self):
        print("Setting up VNA windows...")
        self.delete_all_traces()
        self.delete_all_windows()
        
        self.create_new_window(1)
        self.create_new_window(2)
        self.create_new_window(3)
        self.create_new_window(4)
        self.add_new_trace(1, "S11", "S11", 1, 1)
        self.add_new_trace(1, "S12", "S12", 2, 1)
        self.add_new_trace(1, "S21", "S21", 3, 1)
        self.add_new_trace(1, "S22", "S22", 4, 1)
        print("...done!\n")
        
        
        
### SAVE DATA #################################################################
        
    def save_data_on_vna(self, file_name, vna_folder_name):
        self.send_message(f"MMEMory:STORe:DATA 'D:/_ANECHOIC_CHAMBER_/{vna_folder_name}/{file_name}.csv','CSV Formatted Data','displayed','DB',-1\r")
        

    def find_folder(self, path:str):
        answer = self.send_message(f"MMEM:CAT? '{path}'\r", return_answerback=True)
        if self.read_answer(answer) == "\"NO CATALOG\"":
            return 0   #either the folder doesn't exist or it has no files (but maybe other folders)
        else:
            return 1   #there are already files in this folder
        
        
        
        
        
        
        
        
        
        
        