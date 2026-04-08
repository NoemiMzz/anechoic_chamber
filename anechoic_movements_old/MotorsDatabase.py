import MotorsDatabase as md
import numpy as np
import time
import os
import os.path
import scipy.interpolate as interpolate
import scipy.optimize as opt
import scipy.stats as spstats
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from colorama import Fore, Back, Style

Motor_1="DMT-200"
Motor_2="LIMES-170"
Motor_3="LMT-80P"

Pos1=0
Pos2=0
Pos3=0

##############################################################################################################

def path(database_name):#check sul percorso con relativo messaggio d'errore

    path= os.getcwd()+database_name
    
    if not os.path.exists(path):
        print(Back.YELLOW + "                                                                                                               ")
        print(Back.RED + "                                                                                                               ")
        print(Back.YELLOW + "                                                                                                               ")
        print(Back.RED + "                                                                                                               ")
        print(Back.YELLOW + "                                                                                                               ")
        print(Back.RED + "                                                                                                               "+Style.RESET_ALL)
        print(Fore.RED +Style.DIM + "                                      WARNING, new path/folder defined !!!")
        print(Fore.RED +Style.DIM + "                                      WARNING, new path/folder defined !!!")
        print(Fore.RED +Style.DIM + "                                      WARNING, new path/folder defined !!!")
        print(Fore.RED +Style.DIM + "                                      WARNING, new path/folder defined !!!")
        print(Back.RED + "                                                                                                               ")
        print(Back.YELLOW + "                                                                                                               ")
        print(Back.RED + "                                                                                                               ")
        print(Back.YELLOW + "                                                                                                               ")
        print(Back.RED + "                                                                                                               ")
        print(Back.YELLOW + "                                                                                                               "+Style.RESET_ALL)
        
    return path

##############################################################################################################

def logbook(database_name):#definizione del database
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    if not os.path.exists(master_folder):
        os.makedirs(master_folder)
        
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    if os.path.exists(master_path)==True: #utile nel caso ci questa funzione vega richiamata in più programmi e/o notebooks
            read_master = open(master_path, "r")
            lines=read_master.readlines()
            last_line=len(lines)
    
            motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
            motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
            motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
            position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
            position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
            position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
            
            read_master.close()
            append_master = open(master_path, "a")
            append_master.write(str(time.ctime())+","+str(motor1)+","+str(motor2)+","+str(motor3)+","+str(position1)+","+str(position2)+","+str(position3)+"\n")
            
            append_master.close()
        
        
    if os.path.exists(master_path)==False: #per generare il database da zero
        append_master = open(master_path, "a")
        append_master.write("Time,Motor Name 1,Motor Name 2,Motor Name 3,Position Motor 1 [deg],Position Motor 2 [mm],Position Motor 3[mm],\n\n")
        append_master.write(str(time.ctime())+","+str(Motor_1)+","+str(Motor_2)+","+str(Motor_3)+","+str(Pos1)+","+str(Pos2)+","+str(Pos3)+"\n")
        
    append_master.close()
    
    return

##############################################################################################################

def get_actual_situation(database_name):#check per osservare l'ultima riga di campi inseriti nel database
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    
    time=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(0), max_rows=1,delimiter=",",dtype = 'str')
    motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
    motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
    motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
    position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
    position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
    position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
    
    print()
    print()
    print("Current Situation:")
    print()
    print("Time of last modification: ",time)
    print(f"Motor: {motor1} at Position: {position1}")
    print(f"Motor: {motor2} at Position: {position2}")
    print(f"Motor: {motor3} at Position: {position3}")
    print()
    read_master.close()
    
    return "Done!"

##############################################################################################################

def get_motor1(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(motor1)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_motor2(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(motor2)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_motor3(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(motor3)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_position1(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position1)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_position2(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position2)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_position3(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
    read_master = open(master_path, "r")
    lines=read_master.readlines()
    last_line=len(lines)
    
    position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position3)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def set_position1(database_name,position1):
    
            master_folder= os.getcwd()+'/'+database_name+'/'
            master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
            read_master = open(master_path, "r")
            lines=read_master.readlines()
            last_line=len(lines)
    
            motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
            motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
            motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
            #position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
            position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
            position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
            #Ogni set_variable è un copia e incolla di questo blocco con la riga associata alla variabile di interesse commentata 
            
            
            read_master.close()
            append_master = open(master_path, "a")
            append_master.write(str(time.ctime())+","+str(motor1)+","+str(motor2)+","+str(motor3)+","+str(position1)+","+str(position2)+","+str(position3)+"\n")
            
            
            append_master.close()
    
            return 

##############################################################################################################

def set_position2(database_name,position2):
    
            master_folder= os.getcwd()+'/'+database_name+'/'
            master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
            read_master = open(master_path, "r")
            lines=read_master.readlines()
            last_line=len(lines)
    
            motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
            motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
            motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
            position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
            #position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
            position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
            #Ogni set_variable è un copia e incolla di questo blocco con la riga associata alla variabile di interesse commentata 
            
            
            read_master.close()
            append_master = open(master_path, "a")
            append_master.write(str(time.ctime())+","+str(motor1)+","+str(motor2)+","+str(motor3)+","+str(position1)+","+str(position2)+","+str(position3)+"\n")
            
            
            append_master.close()
    
            return 

##############################################################################################################

def set_position3(database_name,position3):
    
            master_folder= os.getcwd()+'/'+database_name+'/'
            master_path=master_folder+'/LogBook_'+database_name+'.csv'
    
            read_master = open(master_path, "r")
            lines=read_master.readlines()
            last_line=len(lines)
    
            motor1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(1), max_rows=1,delimiter=",",dtype = 'str')
            motor2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(2), max_rows=1,delimiter=",",dtype = 'str')
            motor3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(3), max_rows=1,delimiter=",",dtype = 'str')
            position1=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
            position2=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
            #position3=np.genfromtxt(master_path, skip_header=last_line-1,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
            #Ogni set_variable è un copia e incolla di questo blocco con la riga associata alla variabile di interesse commentata 
            
            
            read_master.close()
            append_master = open(master_path, "a")
            append_master.write(str(time.ctime())+","+str(motor1)+","+str(motor2)+","+str(motor3)+","+str(position1)+","+str(position2)+","+str(position3)+"\n")
            
            
            append_master.close()
    
            return 

##############################################################################################################

def back_up_file(database_name,position1,position2,position3): 
            
            master_folder= os.getcwd()+'/'+database_name+'/'
            
            backup_path=master_folder+'/BackupFile_'+database_name+'.txt'
            
            append_master = open(backup_path, "w")
            
            append_master.write(str(time.ctime())+","+str(Motor_1)+","+str(Motor_2)+","+str(Motor_3)+","+str(position1)+","+str(position2)+","+str(position3)+"\n")
                        
            append_master.close()
    
            return 

#registra l'intenzione di movimento, una volta arrivato a destinazione lo spostamento viene riportato nel logbook

##############################################################################################################

def get_back_up_position1(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/BackupFile_'+database_name+'.txt'
    
    position1=np.genfromtxt(master_path,usecols=(4), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position1)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_back_up_position2(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/BackupFile_'+database_name+'.txt'
    
    position2=np.genfromtxt(master_path,usecols=(5), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position2)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################

def get_back_up_position3(database_name):#per ottenere il valore e o la striga dell'ultima riga del campo desiderato
    
    master_folder= os.getcwd()+'/'+database_name+'/'
    master_path=master_folder+'/BackupFile_'+database_name+'.txt'
    
    position3=np.genfromtxt(master_path,usecols=(6), max_rows=1,delimiter=",",dtype = 'str')
    
    return str(position3)#consiglio di salvare e leggere sempre strighe e fare il casting in un secondo momento, a volte ho avuto problemi nella lettura (genfromtxt richiede il tipo di dato che leggerà..)

##############################################################################################################