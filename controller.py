from motor import Motor
import socket

#%%
class Controller:
    
    def __init__(self,
                 ip_addr="169.254.217.26",
                 port=8777
                 ):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port))
        print("Connected to motors socket!\n")
        
        self.motor = {}
        
        for axis in range(1,10):
            try:
                mot = Motor(self.socket, axis)
                self.motor[axis] = mot
                print(f"Found the {mot.motor_name()} on axis {axis}")
            except RuntimeError:
                print(f"No motor connected on axis {axis}")
        print()
        
        self.mot_axis = list(self.motor.keys())

        
        
### POSITION ##################################################################
      
    ### go to position ###          
    def go_to(self, position_list:list):
        
        if not len(position_list) == len(self.mot_axis):
            raise Exception("The position list length must match the number of connected motors")
            
        for ax, pos in zip(self.mot_axis, position_list):
            self.socket.send(f"PSET{ax}={pos * self.motor[ax].step_scale}\r".encode())

        mot_go = ''
        for axis in range(9, 0, -1):
            print(axis, self.mot_axis)
            if axis in self.mot_axis:
                mot_go += '1'
            else:
                mot_go += '0'
        print(mot_go)
        #self.socket.send(f"MPGO={mot_go}\r".encode())
        self.socket.send(f"MPGO=000000111\r".encode())
        
        self.wait_stop()
        
        
    ### wait for all motors to arrive at the set position
    def wait_stop(self):
        for mot in self.motor.values():
            mot.wait_stop()
            
            
    ### read the position of all the motors from the encoder ###
    def read_position(self, print_pos=False):
        pos_all = []
        for mot in self.motor.values():
            pos = mot.read_position()
            pos_all.append(pos)
            if print_pos:
                print(f"{mot.motor_name()}: {pos}{mot.motor_udm()}")
        return pos_all
            
            
    ### set a new zero encoder position for all motors ###
    def set_zero_position(self):
        for mot in self.motor.values():
            mot.set_zero_position()
            
            
            
### MODE ######################################################################

    ### switch all from absolute to relative ###
    def abs_to_rel(self):
        for mot in self.motor.values():
            mot.abs_to_rel()
     
        
    ### switch all from relative to absolute ###
    def rel_to_abs(self):
        for mot in self.motor.values():
            mot.rel_to_abs()










