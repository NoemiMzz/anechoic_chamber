import VNA_Remote_Control as vna
import Motors_Remote_Control_Ethernet as mrc
import MotorsDatabase as md

from datetime import datetime
import time
import os
import numpy as np

import argparse
import __main__ as main
def uniquify(path):
    """
    Returns a unique path by appending a 3-digit counter to the original path
    until it finds a path that does not exist.

    Parameters
    ----------
    path : str
        The original path to uniquify.

    Returns
    -------
    unique_path : str
        The uniquified path.
    """
    counter = 0
    while os.path.isdir(path + "_" + f"{counter:03d}"):      
        counter += 1
    path = path + "_" + f"{counter:03d}"
    return path

def make_folder_names(args, dirpath):
    """
    Create a set of folder names for storing the output of the script.
    
    Parameters
    ----------
    args : argparse.Namespace
        The command line arguments. Must have the following attributes:
        - iteration : int
            The number of times to repeat the measurement.
        - output_dir : str
            The folder to store the output in. If not specified, the current
            working directory is used.
    dirpath : str
        The base name of the folder to create.
    
    Returns
    -------
    VNA_folder_names : dict
        A dictionary with the folder names to use on the VNA. The keys are the iteration numbers, the values are the folder names.
    pc_folder_names : dict
        A dictionary with the folder names to use on the PC. The keys are the iteration numbers, the values are the folder names.
    """
    pc_folder_names={}
    VNA_folder_names={}
    for it in range(args.iteration):
        VNA_folder_name=dirpath

        if args.output_dir != "":
            pc_folder_name=os.path.join(args.output_dir, dirpath)
        else:
            pc_folder_name=dirpath

        VNA_folder_name = uniquify(VNA_folder_name)
        pc_folder_name = uniquify(pc_folder_name)

        if not os.path.isdir(pc_folder_name):
            os.mkdir(pc_folder_name)

        VNA_folder_names[it]=VNA_folder_name
        pc_folder_names[it]=pc_folder_name

    return pc_folder_names, VNA_folder_names

if __name__=="__main__":

    #define VNA Settings
    start_freq=75 #0.01 #in GHz
    stop_freq=110 #in GHz
    IF_bandwidth=100 #in Hz
    point_sweep="1" #1 ON, 0 OFF

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--starting-ang", help="Starting angle position (Deg)", type=float, default=20)
    parser.add_argument("-e", "--ending-ang", help="Ending angle position (Deg). Default:None. If None, the ending is set as -(starting_ang).", type=float, default=None)
    parser.add_argument("-a", "--angle-res", help="Angle resolution (Deg)", type=float, default=1)
    parser.add_argument("-f", "--freq-res", help="Frequency resolution (GHz)", type=float, default=1)
    parser.add_argument("-i", "--iteration", help="Number of iteration of the scan", type=int, default=1)
    parser.add_argument("-p", "--plot", help="Visibility plots", action="store_true")
    parser.add_argument("-n", "--name", help="Name of the scan", type=str, default="")
    parser.add_argument("-o", "--output-dir", help="Output folder", type=str, default="")
    args = parser.parse_args()

    #Set folder name
    if args.name != "":
        name = args.name
    else:
        name = os.path.splitext(main.__file__)[0]
    dirpath=f"{datetime.now().strftime('%Y_%m_%d')}_{name}"
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    pc_folder_names, VNA_folder_names = make_folder_names(args, dirpath)

    #create log file of the scan:
    file = open(os.path.join(args.output_dir, f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_log_scan.txt"),'w')
    file.write(f"freq resolution: {args.freq_res} GHz \n")
    file.write(f"ang resolution: {args.angle_res}° \n")
    file.write(f"number of freq sweep per angle: {args.iteration} \n")
    file.write(f"range of scan: {args.starting_ang}°, {args.ending_ang}° \n")
    file.write(f"folder names: \n")
    for fn in pc_folder_names.values():
        file.write(f"{fn} \n")
    file.close()

    #set number of frequencies
    N_freq = int(len(np.arange(start_freq, stop_freq, args.freq_res))) + 1

    #set number of angle positions
    starting_ang=args.starting_ang #in deg
    if not args.ending_ang:
        ending_ang=-starting_ang
    else:
        ending_ang=args.ending_ang
        
    N_ang = int(abs(starting_ang - ending_ang)/args.angle_res) + 1

    #set VNA and motors settings
    vna.vna_settings(start_freq, stop_freq, IF_bandwidth, N_freq, point_sweep)
    md.logbook(dirpath)
    mrc.motors_settings()
    mrc.start_mot1(dirpath, -starting_ang, N_ang)

    start_scan = time.time()
    # #beam pattern's scan
    for n in range(N_ang):
        mrc.scan_mot1(dirpath, starting_ang, N_ang)       
        ang_pos = -round(-starting_ang+n*abs(starting_ang - ending_ang)/(N_ang-1), 2) 
        print(f"Motor 1 Position= {ang_pos} deg")

        for it in range(args.iteration):
            pc_folder_name, VNA_folder_name = pc_folder_names[it], VNA_folder_names[it]
            print(f"SCAN {it+1}/{args.iteration}")
            print(f"STARTING SCAN WITH ANGLE_RES={args.angle_res:.2f} AND FREQ_RES={args.freq_res:.2f}")
            print(f"FILES SAVED IN {pc_folder_name}")
            vna.make_vna_directory(VNA_folder_name) #se la cartella esiste già, lascia quella precedente

            vna.measure(VNA_folder_name, ang_pos) #se il file esiste già, lascia quello precedente
            vna.transfer_from_vna_to_pc(VNA_folder_name, ang_pos, pc_folder_name) #funziona solo se il file <20 MB
    end_scan = time.time()

    print(f"Scan took {end_scan-start_scan}s")
    
    mrc.reset_mot1(dirpath,-starting_ang,N_ang)

    # #mrc.move_mot1(dirpath, starting_ang, N_ang, VNA_folder_name, pc_folder_name) 
    mrc.reset_all_mot(dirpath) #first reset rotary plate pos then linear axis pos

    # if args.plot:
    #     print("DO PLOT")