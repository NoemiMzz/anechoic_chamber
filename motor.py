import time

#ip_addr = "169.254.217.26"
#port = 8777
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((ip_addr, port))


#%%
class Motor:
    
    def __init__(self,
                 socket,
                 axis
                 ):
        self.socket = socket
        self.axis = axis
        
        #initialize motor
        self.socket.send(f"INIT{self.axis}\r".encode())
        
        #read and save motor code
        self.motor_code = self.read_motor_code()
        
        if self.motor_code == "MpCanErr\r" or self.motor_code == "NoOWISId\r":
            raise RuntimeError(f"CRITICAL: No motor found on axis: {self.axis}")
            
        #compute step scale
        self.step_scale = self.compute_step_scale()
        
        #initialize max velocity
        self.set_safe_velocity()
        
        
        
### PARAMETERS ################################################################

    ### retrieve the motor code ###
    def read_motor_code(self):
        self.socket.send(f"?READOWID{self.axis}=0\r".encode())
        time.sleep(1)
        motor_code = (self.socket.recv(64)).decode()
        return motor_code[:11]


    ### retrives the motor type ###
    def read_motor_type(self):
        self.socket.send(f"?MOTYPE{self.axis}\r".encode())
        motype = int((self.socket.recv(16)).decode())
        if motype == 0:
            return 'DC brush'
        if motype == 2:
            return 'Step motor Open Loop'
        if motype == 3:
            return 'Step motor Closed-Loop'
        if motype == 4:
            return 'BLDC'
        else:
            return 'ERROR - Unknown answer'
            
            
    ### compute the conversion between motor steps and mm/° ###
    def compute_step_scale(self):
        if self.motor_code == '41.085.30AD':   #LTM80P_300 (295mm linear actuator)
            n = 200   #steps per motor revolution from manual
            h = 1   #spindle pitch from manual
            m = self.read_microstep()
            return n * m / h
        if self.motor_code == '41.171.006G':   #LIME170_1000 (1000mm linear actuator)
            n = 200   #steps per motor revolution from manual
            h = 5   #spindle pitch from manual
            m = self.read_microstep()
            return n * m / h
        if self.motor_code == '42.N00.30BV':   #HVM100N_30 (elevation stage)
            n = 200   #steps per motor revolution from manual
            r = 0.5   #travel in mm per motor resolution from manual
            m = self.read_microstep()
            return n * m / r
        if self.motor_code == '43.201.90AG':   #DMT200N_D90 (z-axis rotator)
            #n = 200   #steps per motor revolution from manual
            r = 0.01   #resolution step motor per full step from manual
            m = self.read_microstep()
            return m / r
        if self.motor_code == '43.100.43AD':   #DMT100_D43 (x-axis rotator)
            #n = 200   #steps per motor revolution from manual
            r = 0.01   #resolution step motor per full step from manual
            m = self.read_microstep()
            return m / r


    ### initialize maximum velocity according to the manual ###
    def set_safe_velocity(self):
        if self.motor_code == '41.085.30AD':   #LTM80P_300 (295mm linear actuator)
            self.set_max_velocity(10 * self.step_scale)
        if self.motor_code == '41.171.006G':   #LIME170_1000 (1000mm linear actuator)
            self.set_max_velocity(80 * self.step_scale)
        if self.motor_code == '42.N00.30BV':   #HVM100N_30 (elevation stage)
            self.set_max_velocity(12 * self.step_scale)
        if self.motor_code == '43.201.90AG':   #DMT200N_D90 (z-axis rotator)
            self.set_max_velocity(30 * self.step_scale)
            self.set_rvel(30 * self.step_scale / 5, 30 * self.step_scale)
        if self.motor_code == '43.100.43AD':   #DMT100_D43 (x-axis rotator)
            self.set_max_velocity(24 * self.step_scale)
            self.set_rvel(-24 * self.step_scale / 5, -24 * self.step_scale)
    
    
    ### assign a recognisable name to each motor ###
    def motor_name(self):
        if self.motor_code == '41.085.30AD':
            return "295mm linear actuator"
        if self.motor_code == '41.171.006G':
            return "1000m linear actuator"
        if self.motor_code == '42.N00.30BV':
            return "elevation stage"
        if self.motor_code == '43.201.90AG':
            return "z-axis rotator"
        if self.motor_code == '43.100.43AD':
            return "x-axis rotator"
        
        
    ### assign a recognisable name to each motor ###
    def motor_udm(self):
        linear = {'41.085.30AD', '41.171.006G', '42.N00.30BV'}
        rotator = {'43.201.90AG', '43.100.43AD'}

        if self.motor_code in linear:
            return " mm"
        if self.motor_code in rotator:
            return "°"
        

### POSITION ##################################################################
    
    ### go to position ###
    def go_to(self, position):
        position = float(position)
        if self.read_mode() == 'RELAT':
            old_position = self.read_position()
        self.socket.send(f"PSET{self.axis}={position * self.step_scale}\r".encode())
        self.socket.send(f"PGO{self.axis}\r".encode())
        
        self.wait_stop()   #wait for the motion to be completed
        
        new_position = self.read_position()

        if self.read_mode() == 'ABSOL':
            if new_position != position:   #print check to be at the right final position
                print(f"Something went wrong :(\nMotor on axis {self.axis} moved to {new_position}{self.motor_udm()} instead of {position}{self.motor_udm()}")
        if self.read_mode() == 'RELAT':
            if new_position != (old_position + position):   #print check to be at the right final position
                print(f"Something went wrong :(\nMotor on axis {self.axis} moved to {new_position}{self.motor_udm()} instead of {old_position + position}{self.motor_udm()}")


    ### go to position in step unit ###
    def go_to_step(self, position):
        if self.read_mode() == 'RELAT':
            old_position = self.read_step_position()
        self.socket.send(f"PSET{self.axis}={position}\r".encode())
        self.socket.send(f"PGO{self.axis}\r".encode())
        
        self.wait_stop()   #wait for the motion to be completed
        
        new_position = self.read_step_position()
        
        if self.read_mode() == 'ABSOL':
            if new_position != position:   #print check to be at the right final position
                print(f"Something went wrong :(\nMotor on axis {self.axis} moved to {new_position} instead of {position}")
        if self.read_mode() == 'RELAT':
            if new_position != (old_position + position):   #print check to be at the right final position
                print(f"Something went wrong :(\nMotor on axis {self.axis} moved to {new_position} instead of {position}")


    ### wait for the motor to arrive at the set position ###
    def wait_stop(self):
        while True:
            self.socket.send("?ASTAT\r".encode())
            status = (self.socket.recv(64)).decode()[self.axis-1]
            if status == "R":
                break
            time.sleep(0.01)
    
    
    ### read the position in step unit from the encoder ###
    def read_step_position(self):
        self.socket.send(f"?CNT{self.axis}\r".encode())
        return int((self.socket.recv(64)).decode())
    
    
    ### read the position from the encoder ###
    def read_position(self):
        return self.read_step_position() / self.step_scale   #in mm or °


    ### set a new zero encoder position ###
    def set_zero_position(self):
        self.socket.send(f"CRES{self.axis}\r".encode())
    


### MODE ######################################################################
     
    ### read if relative or absolute mode ###
    def read_mode(self):
        self.socket.send(f"?MODE{self.axis}\r".encode())
        return ((self.socket.recv(64)).decode())[:5]
        #switching mode changes only the interpretation of .go_to(), not the position


    ### switch from absolute to relative ###
    def abs_to_rel(self):
        if self.read_mode() == 'RELAT':
            print(f"Axis {self.axis} already in RELATIVE mode")
        else:
            self.socket.send(f"RELAT{self.axis}\r".encode())
            print(f"Axis {self.axis} set to RELATIVE mode")
            
            
    ### switch from relative to absolute ###
    def rel_to_abs(self):
        if self.read_mode() == 'ABSOL':
            print(f"Axis {self.axis} already in ABSOLUTE mode")
        else:
            self.socket.send(f"ABSOL{self.axis}\r".encode())
            print(f"Axis {self.axis} set to ABSOLUTE mode")
        


### VELOCITY ##################################################################
    
    ### read/set the maximum travel velocity ###
    def set_max_velocity(self, velocity):
        self.socket.send(f"PVEL{self.axis}={velocity}\r".encode())
        
    def read_max_velocity(self):
        self.socket.send(f"?PVEL{self.axis}\r".encode())
        return int((self.socket.recv(64)).decode())
    
    
    ### read/set the maximum velocty to reach the reference switch ###
    def set_rvel(self, vel_slow, vel_fast):
        self.socket.send(f"RVELS{self.axis}={vel_slow}\r".encode())
        self.socket.send(f"RVELF{self.axis}={vel_fast}\r".encode())
        
    def read_rvel(self):
        self.socket.send(f"?RVELS{self.axis}\r".encode())
        vel_slow = int((self.socket.recv(64)).decode())
        self.socket.send(f"?RVELF{self.axis}\r".encode())
        vel_fast = int((self.socket.recv(64)).decode())
        return vel_slow, vel_fast
    


### MICROSTEP #################################################################

    ### read/set the number of microsteps per full-step ###
    def set_microstep(self, microstep):
        self.socket.send(f"MCSTP{self.axis}={microstep}\r".encode())
        
    def read_microstep(self):
        self.socket.send(f"?MCSTP{self.axis}\r".encode())
        return int((self.socket.recv(64)).decode())
        
    
    
### REFERENCE #################################################################
    
    ### frees the motor from the limit switch/brake ###    
    def free_motor(self):
        self.socket.send("?ASTAT\r".encode())
        status = (self.socket.recv(64)).decode()[self.axis-1]
        if status == 'L' or status == 'B':
            self.socket.send(f"EFREE{self.axis}\r".encode())
            print(f"Axis {self.axis} is now free from the limit switch/brake")
        else:
            print(f"Axis {self.axis} isn't stuck at the limit switch/brake")
            
            
    ### set reference switch ###
    def set_reference_switch(self, ref_number:int):
        if not (0 <= ref_number < 4):
            raise IndexError("Reference index out of range")
        mask = '0000'
        mask = mask[:ref_number] + '1' + mask[ref_number+1:]
        self.socket.send(f"RMK{self.axis}={mask}\r".encode())
    
    
    ### read reference switch ###
    def read_reference_switch(self):
        self.socket.send(f"?RMK{self.axis}\r".encode())
        return (self.socket.recv(64)).decode()
    
    
    ### reach the reference limit switch ###
    def reach_limit_switch(self, print_pos=False):
        supported_motors = {'43.100.43AD', '43.201.90AG'}   #function for the rotors only
        if self.motor_code not in supported_motors:
            raise ValueError(f"The {self.motor_name} does not support reaching the limit switch")

        self.socket.send(f"REF{self.axis}=1\r".encode())
        self.wait_stop()
        if print_pos:
            print(f"Limit switch reached!\nPosition = {self.read_position()}{self.motor_udm()}")


    ### set the limit switch as zero position ###
    def set_zero_limit_switch(self, print_pos=False):
        supported_motors = {'43.100.43AD', '43.201.90AG'}   #function for the rotors only
        if self.motor_code not in supported_motors:
            raise ValueError(f"The {self.motor_name} does not support reaching the limit switch")
        
        self.reach_limit_switch(print_pos)
        self.set_zero_position()
        if print_pos:
            print("--- New zero position set ---")



#%%
###############################################################################

class LTM80P_300(Motor):   #295mm linear actuator
    def __init__(self,
                 socket,
                 axis):
        Motor.__init__(self, socket, axis)
        
        if self.motor_code != '41.085.30AD':
            raise ValueError(f"--- WRONG MOTOR CONNECTED TO AXIS {self.axis} ---\nThe initialized motor model does not match the one connected to axis {self.axis}")
    


#%%
###############################################################################

class LIME170_1000(Motor):   #1000mm linear actuator
    def __init__(self,
                 socket,
                 axis):
        Motor.__init__(self, socket, axis)
        
        if self.motor_code != '41.171.006G':
            raise ValueError(f"--- WRONG MOTOR CONNECTED TO AXIS {self.axis} ---\nThe initialized motor model does not match the one connected to axis {self.axis}")
    


#%%
###############################################################################

class HVM100N_30(Motor):   #elevation stage
    def __init__(self,
                 socket,
                 axis):
        Motor.__init__(self, socket, axis)
        
        if self.motor_code != '42.N00.30BV':
            raise ValueError(f"--- WRONG MOTOR CONNECTED TO AXIS {self.axis} ---\nThe initialized motor model does not match the one connected to axis {self.axis}")

    

#%%
###############################################################################

class DMT200N_D90(Motor):   #z-axis rotator
    def __init__(self,
                 socket,
                 axis):
        Motor.__init__(self, socket, axis)
        
        if self.motor_code != '43.201.90AG':
            raise ValueError(f"--- WRONG MOTOR CONNECTED TO AXIS {self.axis} ---\nThe initialized motor model does not match the one connected to axis {self.axis}")

    
    
#%%
###############################################################################

class DMT100_D43(Motor):   #x-axis rotator
    def __init__(self,
                 socket,
                 axis):
        Motor.__init__(self, socket, axis)
        
        if self.motor_code != '43.100.43AD':
            raise ValueError(f"--- WRONG MOTOR CONNECTED TO AXIS {self.axis} ---\nThe initialized motor model does not match the one connected to axis {self.axis}")

        
        
        
        
        
        
            