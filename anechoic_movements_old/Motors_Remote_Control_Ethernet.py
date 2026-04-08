import time
import socket
import numpy as np
import Motors_Remote_Control_Ethernet as mrc
import MotorsDatabase as md
import VNA_Remote_Control as vna

HOST = "169.254.217.26"
PORT = 8777

stepscale_mot1=5000
stepscale_mot2=2000
stepscale_mot3=10000

##############################################################################################################

def initialize_motor():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        s.send("INIT1\r".encode()) #Enable the motor power stage, release and activate position control loop
        s.send("INIT2\r".encode())
        s.send("INIT3\r".encode())

        print("Motors ready!")
        
        s.close()
      
    return

##############################################################################################################

def set_velocity(): #nel caso si volessero cambiare le velocità,bisogna vedere se stanno nei LIMITI di velocità dei motori
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send("VVEL1=300000\r".encode())
        s.send("VVEL2=300000\r".encode())
        s.send("VVEL3=300000\r".encode())
    
        print("Motors velocities set!")
        
        #s.send("VGO1\r".encode())  #comandi per dare via ai motori alla velocità settata (ma non regolo la posizione)
        #s.send("VGO2\r".encode())
        #s.send("VGO3\r".encode())
           
        s.close()
    
    return

##############################################################################################################

def set_movement_type(): 
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
    
        #PMOD<n>=0 = trapezoidal proﬁling mode, 1 = S-curve proﬁling mode
        
        s.send("PMOD1=1\r".encode())
        s.send("PMOD2=1\r".encode())
        s.send("PMOD3=1\r".encode())
        
        print("Movement type set!")
        
        s.close()
    
    return

##############################################################################################################

def coordinates_settings(): 
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
    
    #i movimenti sono relativi alla posizione precedente, esiste anche l'opzione assoluta, ma si resetta ad ogni spegnimento del PS90+
    
        s.send("RELAT1\r".encode())
        s.send("RELAT2\r".encode())
        s.send("RELAT3\r".encode())

    
        print("Coordinate settings defined!")
        print()
        
        s.close()   
    
    return

##############################################################################################################

def motors_settings(): 
    
    mrc.initialize_motor()
    mrc.set_velocity()
    mrc.set_movement_type()
    mrc.coordinates_settings()
    
    return

##############################################################################################################

def move_mot1(database_name,start,N,VNA_folder_name,Pc_folder): 
    
    md.logbook(database_name)
    mrc.motors_settings()
    vna.make_vna_directory(VNA_folder_name) #se la cartella esiste già, lascia quella precedente
    
    mrc.start_mot1(database_name,-start,N)
    
    for i in range(N):
        
        mrc.scan_mot1(database_name,-start,N)        
        print(f"Motor 1 Position= {-round(-start+i*2*abs(start)/(N-1),2)} deg")
        vna.measure(VNA_folder_name,-round(-start+i*2*abs(start)/(N-1),2)) #se il file esiste già, lascia quello precedente
        vna.transfer_from_vna_to_pc(VNA_folder_name,-round(-start+i*2*abs(start)/(N-1),2),Pc_folder) #funziona solo se il file <20 MB
        
    mrc.reset_mot1(database_name,-start,N)
    
    return

##############################################################################################################

def start_mot1(database_name,start,N): 
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET1={stepscale_mot1*start-2*abs(start)/(N-1)*stepscale_mot1}\r".encode())
        s.send("PGO1\r".encode())
        
        s.close()  
    
        while(mrc.astat(database_name)[2]!='R'):
                time.sleep(0.5)
    
        md.set_position1(database_name,round(float(md.get_position1(database_name))+start-2*abs(start)/(N-1),2))
    
        print("Beam Pattern scan is starting!")
    
        time.sleep(3)
        print()
    
    return

##############################################################################################################

def test_mot1(database_name,start,N): 

    print(f"PSET1={2*abs(start)/(N-1)*stepscale_mot1}\r".encode())    
    return
        
############################################################################################################## 


##############################################################################################################

def scan_mot1(database_name,start,N): 
                
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET1={2*abs(start)/(N-1)*stepscale_mot1}\r".encode())
        s.send("PGO1\r".encode())
        
        s.close()        
    
        while(mrc.astat(database_name)[2]!='R'):
            time.sleep(0.5)
        
        md.set_position1(database_name,round(float(md.get_position1(database_name))+2*abs(start)/(N-1),2))
            
    return
        
############################################################################################################## 

def reset_mot1(database_name,start,N): 
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))    
        
        s.send(f"PSET1={-float(md.get_position1(database_name))*stepscale_mot1}\r".encode())
        s.send("PGO1\r".encode())
        
        s.close()

        while(mrc.astat(database_name)[2]!='R'):
            time.sleep(0.5)
    
        md.set_position1(database_name,0)
    
        print()
        print("Ready for another scan!")
        
        vna.cont_sweep()
     
    return

##############################################################################################################

def alignment_mot1(database_name,posizione1):
    
    md.logbook(database_name)
    mrc.motors_settings()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET1={-stepscale_mot1*posizione1}\r".encode())
        s.send("PGO1\r".encode())
        
        s.close()

        while(mrc.astat(database_name)[2]!='R'):
            time.sleep(0.5)
    
        md.set_position1(database_name,float(md.get_position1(database_name))+posizione1)
    
        print(f"Reciever position shifted by {md.get_position1(database_name)} deg!")
        print("Check VNA signal!")
    
    return

##############################################################################################################

def move_mot2and3(database_name,posizione2,posizione3): 
    
    md.logbook(database_name)
    mrc.motors_settings()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET2={posizione2*stepscale_mot2}\r".encode())
        s.send(f"PSET3={posizione3*stepscale_mot3}\r".encode())
        s.send("PGO2\r".encode())
        s.send("PGO3\r".encode())
        
        s.close()

        print("Motors 2 and 3 are moving!")
 
        while(mrc.astat(database_name)[3]!='R'):
            time.sleep(0.5)
        
        md.set_position2(database_name,float(md.get_position2(database_name))+posizione2)
    
        print(f"Motor 2 is arrived at {md.get_position2(database_name)} mm!")
    
        while(mrc.astat(database_name)[4]!='R'):
            time.sleep(0.5)
    
        md.set_position3(database_name,float(md.get_position3(database_name))+posizione3)
    
        print(f"Motor 3 is arrived at {md.get_position3(database_name)} mm!")
        
        md.get_actual_situation(database_name)
    
    return

##############################################################################################################

def reset_all_mot(database_name): 
    
    md.logbook(database_name)
    mrc.motors_settings()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET1={-float(md.get_back_up_position1(database_name))*stepscale_mot1}\r".encode())
        s.send("PGO1\r".encode())
        
        s.close()
    
        print("Motors 1 is returning home!")
    
        while(mrc.astat(database_name)[2]!='R'):
            time.sleep(0.5)
    
        md.set_position1(database_name,0)
    
        print("Motor 1 is returned home!")
    
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET2={-float(md.get_back_up_position2(database_name))*stepscale_mot2-5*stepscale_mot2}\r".encode())
        s.send(f"PSET3={-float(md.get_back_up_position3(database_name))*stepscale_mot3-5*stepscale_mot3}\r".encode())
        s.send("PGO2\r".encode())
        s.send("PGO3\r".encode())
        
        s.close()
    
        #il -5*stepscale_mot (5 mm) è per correggere gli errori di posizionamento che si accumulerebbero dopo n movimenti
    
        print("Motors 2 and 3 are returning home!")
    
        while(mrc.astat(database_name)[3]!='R'):
            time.sleep(0.5)
    
        md.set_position2(database_name,0)
    
        print("Motor 2 is returned home!")
       
        while(mrc.astat(database_name)[4]!='R'):
            time.sleep(0.5)
    
        md.set_position3(database_name,0)
    
        print("Motor 3 is returned home!")
    
        md.get_actual_situation(database_name)
    
    return

##############################################################################################################
        
def astat(database_name):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send("?ASTAT\r".encode()) #9 caratteri che descrive lo status dei motori (gli ultimi 6 dovrebbero essere U se inutilizzati)
        time.sleep(0.5)
        astat=s.recv(1024) #per un qualsiasi messaggio porta i byte a 128
        
        s.send("?CNT1\r".encode())
        time.sleep(0.5)
        cnt1=s.recv(1024).decode()
        
        s.send("?CNT2\r".encode())
        time.sleep(0.5)
        cnt2=s.recv(1024).decode()
        
        s.send("?CNT3\r".encode())
        time.sleep(0.5)
        cnt3=s.recv(1024).decode()
        
        cnt1=float(cnt1)
        cnt2=float(cnt2)
        cnt3=float(cnt3)
        
        md.back_up_file(database_name, cnt1/stepscale_mot1, cnt2/stepscale_mot2, cnt3/stepscale_mot3)
        
        s.close()
        
    return str(astat)

#la stringa che ritorna è "b'RRRUUUUUU\r'", quindi il carattere del primo motore è quello all'indice 2,quello del secondo è il 3 e quello del terzo è il 4

##############################################################################################################

def move_mot3(database_name,posizione3): 
    
    md.logbook(database_name)
    mrc.motors_settings()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        
        s.send(f"PSET3={posizione3*stepscale_mot3}\r".encode())
        s.send("PGO3\r".encode())
        
        s.close()
        
        print("Motor 3 is moving!")
        
        while(mrc.astat(database_name)[4]!='R'):
            time.sleep(0.5)
    
        md.set_position3(database_name,float(md.get_position3(database_name))+posizione3)
    
        print(f"Motor 3 is arrived at {md.get_position3(database_name)} mm!")
        
        md.get_actual_situation(database_name)
    
    return

##############################################################################################################