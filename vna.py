import time
import socket

#ip_addr = "169.254.217.24"
#port = 5024


#%%
class VNA:
    def __init__(self,
                 start_freq,
                 stop_freq,
                 IF_bandwidth,
                 ip_addr="169.254.217.24",
                 port=5024
                 ):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port))
        print("Connected to VNA socket!\n")
        
        self.set_bandwidth(start_freq, stop_freq) #GHz
        
        self.set_IF_bandwidth(IF_bandwidth) #Hz
        
        self.point_sweep_ON() #check if to set on or off as default !!!
        
        self.standard_windows_setup()
        


###############################################################################

    ### send a command to the VNA ###
    def send_message(self, message, return_answerback=False):
        self.socket.send(message.encode())
        time.sleep(0.2)
        answerback = self.socket.recv(1024).decode()
        if return_answerback:
            return answerback
        
        
        
### FREQUENCY #################################################################
    
    ### set start and stop frequency for different bands ###
    def set_startfreq(self,start_freq):
        self.send_message(f"SENS:FREQ:STAR {start_freq * 10**9}\r") #GHz
        
    def set_stopfreq(self, stop_freq):
        self.send_message(f"SENS:FREQ:STOP {stop_freq * 10**9}\r") #GHz
    
    def set_bandwidth(self, start_freq, stop_freq):
        self.set_startfreq(start_freq)
        self.set_stopfreq(stop_freq)
    
    ### set IF bandwidth ###
    def set_IF_bandwidth(self, IF_bandwidth):
        self.send_message(f"SENS:BWID {str(IF_bandwidth)} HZ\r") #Hz
        
        
        
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
    
    ### number of points/sweeps to average ###
    def set_average_count(self, count:int):
        self.send_message(f"SENS:AVER:COUN {count}\r")
        
        
        
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
        
    ### sweep continuously ###
    def continuous_sweep(self):
        self.send_message("SENS:SWE:MODE CONT\r")
        
        
        
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
        
        
        
### SAVE DATA #################################################################
        
    def save_data_on_vna(self, file_name, vna_folder_name):
        self.send_message(f"MMEMory:STORe:DATA 'D:/{vna_folder_name}/{file_name}.csv','CSV Formatted Data','displayed','DB',-1\r")
        
        
        
        
        
        
        
        
        
        
        
        
        