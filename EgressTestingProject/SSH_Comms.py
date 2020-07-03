# -*- coding: utf-8 -*-

"""
Numen Ct-Voltage Calibration (Collector Commands)
Made by Connor Gregory on 04/12/18
"""
import paramiko
import os
import pandas as pd
import numpy as np
import select
import re
import operator as op
import time
from time import gmtime, strftime
from scp import SCPClient

"""
User Defined Variables
"""
cwd = dir_path = os.path.dirname(os.path.realpath(__file__)) #'C:\\Users\\conno\\source\\repos\\VoltageCalibration\\VoltageCalibration'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
port = '1257'
key_path = ("%s%s") % (cwd,'\\SSH_Key\\numen_collector_ssh')
#">ssh -i \.ssh\numen_collector_ssh root@10.0.0.96 -p 1257 "export PATH=\"/usr/bin:/usr/local/bin:/sbin:/bin:/usr/sbin\" && python EgressTestV2.py""

"""
Helper Functions for SSH Comms
"""
CommandInfo = pd.DataFrame( columns= ['Command_Sent', 'Response_Raw', 'Error_log','Message_log'])
class SSH():

        #%% Send Commands Function
    def SendCommand (self, command):
        global CommandInfo
        EnvDict = {"PATH":"/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"}
        response = ""
        try: 
            print(" %s \n" % command)
            # Send the command (non-blocking) (string data in, out, error)
            stdin, stdout, stderr = ssh.exec_command(command, timeout= 15)
    
        # Wait for the command to terminate
            while not stdout.channel.exit_status_ready():
            # Only print data if there is data to read in the channel
                if stdout.channel.recv_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if len(rl) > 0:

                    # Print data from stdout
                        response = stdout.read().decode("utf-8")
                        print(response)           
            out_log_all = stdout.read().decode()
            err_log_all = stderr.read().decode()
            print(err_log_all)
            CommandInfo = CommandInfo.append({'Command_Sent': command, 'Response_Raw': response, 'Error_log': err_log_all, 'Message_log': out_log_all}, ignore_index=True)
            return response
        except:
            print("fix this.... god damn")
#            if stdout.channel.recv_ready():
 #               if len(strerr) > 0:
  #               print (stderr.read())
                   #print('Fatal Error, could not execute command error log: ' + err_log_all)          
           #print(response); 
            return;
    #%% Connect to host
    def Connect(self, hostname):
        try:
            ssh.connect(hostname,
                        port = port,
                        username = 'root',
                        key_filename = key_path,
                        )
            print("\nConnected to %s.............\n" % hostname)
    
        except:
            print("could not connect to %s" % hostname)
            return;

    #%% Progress for file transfer
    def progress(filename, size, sent):
            sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100))
            return()

    #%% SCP communications to send appropriate files to collector
    def sendSCP(self, local, remote):
        complete = 0
    
        try:
            scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.put(files = local, remote_path = remote)
            print("---------------------------------------------------\n")
            print("File Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            print("SCP didnt work") 
            
            
            complete = 1
    
        return(complete)

        #%% SCP communications to get appropriate files from collector
    def getSCP(self, local, remote):
        complete = 0
    
        try:
            scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.get(remote_path = remote, local_path = local)
            print("---------------------------------------------------\n")
            print("File Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            print("SCP didnt work") 
           
            complete = 1
    
        return(complete)

    def sendDirectorySCP(self, local, remote):
        complete = 0
    
        try:
            scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.put(files = local, remote_path = remote, recursive = True)
            print("---------------------------------------------------\n")
            print("Directory Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            print("SCP didnt work") 
            complete = 1
    
        return(complete)
      




