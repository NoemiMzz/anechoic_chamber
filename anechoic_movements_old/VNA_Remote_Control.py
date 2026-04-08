#versione 15/02/2024


import socket
import os
import os.path
import time
import VNA_Remote_Control as vna


HOST = "169.254.217.24"
PORT = 5024

# CALC funge solo per GPIB (è scritto all'inizio di Memory...)
#Mancano:-Marker
        #-Data--->Memory
    
##############################################################################################################

def lib_test():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto  
            
        s.send("*IDN?\r".encode())
        
        time.sleep(0.2)
        data=s.recv(1024).decode()
        print(data[len("*IDN?\r\n"):-7])
        
        s.close()
    return
    
##############################################################################################################

def set_start_freq(Start_Freq):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:FREQ:STAR {Start_Freq*10**9}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
        
        print(f"Start Frequency: {Start_Freq} GHz")
            
        s.close()
        
    return

##############################################################################################################

def set_stop_freq(Stop_Freq):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:FREQ:STOP {Stop_Freq*10**9}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
        
        print(f"Stop Frequency: {Stop_Freq} GHz")
            
        s.close()
        
    return

##############################################################################################################

def set_IF_bwid(IF_Bandwidth):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:BWID {str(IF_Bandwidth)} HZ\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
        
        print(f"IF Bandwidth: {IF_Bandwidth} Hz")

        s.close()
    
    return

##############################################################################################################

def set_num_point(Num_Point):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:POIN {Num_Point}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
        
        print(f"Number of points per file: {Num_Point}")
            
        s.close()
    
    return

##############################################################################################################

def set_avg_status(Avg_Status):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:AVER {Avg_Status}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def set_avg_mode(Avg_Mode):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:AVER:MODE {Avg_Mode}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def set_avg_points(Avg_Points):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:AVER:COUN {Avg_Points}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def clear_avg():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:AVER:CLE\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def set_sweep_sequence(Point_Sweep):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:GEN:POIN {Point_Sweep}\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        if (Point_Sweep=="1"):
            print("Point to point sweep mode: ON")
        elif (Point_Sweep=="0"):
            print("Point to point sweep mode: OFF")
        else:
            print("Invalid entry, please retry")
            
        s.close()
    
    return

##############################################################################################################

def make_vna_directory(VNA_folder_name):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'mmemory:mdirectory "D:/{VNA_folder_name}"\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def vna_settings(Start_Freq,Stop_Freq,IF_Bandwidth,Num_Point,Point_Sweep):
    
    vna.set_start_freq(Start_Freq)
    vna.set_stop_freq(Stop_Freq)
    vna.set_IF_bwid(IF_Bandwidth)
    vna.set_num_point(Num_Point)
    vna.set_sweep_sequence(Point_Sweep)
    
    return

##############################################################################################################

def measure(VNA_folder_name,File_Name):

    vna.hold_sweep()
    while(vna.sweep_mode_check()!="HOLD"):
        time.sleep(1)
        
    print("Hold Mode secured")

    vna.single_sweep()
    while(vna.sweep_mode_check()!="HOLD"):
        time.sleep(1)
        
    print("First Sweep Done!")

    vna.single_sweep()
    while(vna.sweep_mode_check()!="HOLD"):
        time.sleep(1)

    print("Measuring...")

    vna.save_cvs_file_on_vna_in_folder(VNA_folder_name,File_Name)

    return
    
##############################################################################################################

def sweep_mode_check():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:MODE?\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024).decode()
            
        s.close()

        status_decoded=data[len("'SENS:SWE:MODE?\r"):-8]      
    
    return status_decoded

#controllo lo stato della modalità di sweep

##############################################################################################################

def single_sweep():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:MODE SING\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

#fa una sweepata dall'inizio e poi va in modalità HOLD. Per un'aquisizione continua CONT.

##############################################################################################################

def hold_sweep():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:MODE HOLD\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

#ferma l'acquisizione, necessario per avere sotto controllo il processo di acquisizione.

##############################################################################################################

def cont_sweep():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'SENS:SWE:MODE CONT\r'.encode())
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

#serve per reimpostare l'acquisizione continua sul VNA.

##############################################################################################################

def save_cvs_file_on_vna_in_folder(VNA_folder_name,File_Name):
    
    name=str(File_Name)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'MMEMory:STORe:DATA "D:/{VNA_folder_name}/{name}.csv","CSV Formatted Data","displayed","DB",-1\r'.encode()) 
        
        time.sleep(0.2)
        data=s.recv(1024)
            
        s.close()
    
    return

##############################################################################################################

def transfer_from_vna_to_pc(VNA_folder_name,File_Name,Pc_folder):
    
    name=str(File_Name)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        time.sleep(0.2)
        s1=s.recv(1024) #check per ovviare a problematiche legate al messaggio di benvenuto
            
        s.send(f'MMEMory:TRANsfer? "D:/{VNA_folder_name}/{name}.csv"\r'.encode())
         
        time.sleep(0.2)    
        vna_data=s.recv(32768)
        
        file_path=os.getcwd()+'/'+Pc_folder+"/"+name+".csv"
        
        if not os.path.exists(os.getcwd()+'/'+Pc_folder):
            os.makedirs(os.getcwd()+'/'+Pc_folder)
    
        if not os.path.exists(file_path):
            VNA_file=open(file_path,"w")
            VNA_file.write(vna_data.decode())
            VNA_file.close()
            print(f"... and File {name} transfered to your pc!")
        else:
            print("File alredy exists!")
        s.close()
        print()
    
    return

##############################################################################################################