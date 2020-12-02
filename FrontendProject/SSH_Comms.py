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

# https://stackoverflow.com/questions/23504126/do-you-have-to-check-exit-status-ready-if-you-are-going-to-check-recv-ready

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
    def __init__(self):
        self.cwd = dir_path = os.path.dirname(os.path.realpath(__file__)) #'C:\\Users\\conno\\source\\repos\\VoltageCalibration\\VoltageCalibration'
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.port = '1257'
        self.key_path = ("%s%s") % (self.cwd,'\\SSH_Key\\numen_collector_ssh')
        ## put inits in here

    def SendCommand(self, cmd, want_exitcode=False):
        timeout = 15
        # one channel per command
        stdin, stdout, stderr = self.ssh.exec_command(cmd) 
        # get the shared channel for stdout/stderr/stdin
        channel = stdout.channel
        # we do not need stdin.
        stdin.close()                 
        # indicate that we're not going to write to that channel anymore
        channel.shutdown_write()      

        # read stdout/stderr in order to prevent read block hangs
        stdout_chunks = []
        stdout_chunks.append(stdout.channel.recv(len(stdout.channel.in_buffer)).decode())###added decode()
        # chunked read to prevent stalls
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready(): 
            # stop if channel was closed prematurely, and there is no data in the buffers.
            got_chunk = False
            readq, _, _ = select.select([stdout.channel], [], [], timeout)
            for c in readq:
                if c.recv_ready(): 
                    stdout_chunks.append(stdout.channel.recv(len(c.in_buffer)).decode())#### added decode()
                    got_chunk = True
                if c.recv_stderr_ready(): 
                    # make sure to read stderr to prevent stall    
                    stderr.channel.recv_stderr(len(c.in_stderr_buffer))  
                    got_chunk = True  
            '''
            1) make sure that there are at least 2 cycles with no data in the input buffers in order to not exit too early (i.e. cat on a >200k file).
            2) if no data arrived in the last loop, check if we already received the exit code
            3) check if input buffers are empty
            4) exit the loop
            '''
            if not got_chunk \
                and stdout.channel.exit_status_ready() \
                and not stderr.channel.recv_stderr_ready() \
                and not stdout.channel.recv_ready(): 
                # indicate that we're not going to read from this channel anymore
                stdout.channel.shutdown_read()  
                # close the channel
                stdout.channel.close()
                break    # exit as remote side is finished and our bufferes are empty

        # close all the pseudofiles
        stdout.close()
        stderr.close()

        if want_exitcode:
            # exit code is always ready at this point
            return (''.join(stdout_chunks), stdout.channel.recv_exit_status())
        return ''.join(stdout_chunks)
            #%% Send Commands Function
    #%% Connect to host
    def Connect(self, hostname):
        try:
            self.ssh.connect(hostname,
                        port = self.port,
                        username = 'root',
                        key_filename = self.key_path,
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
            scp = SCPClient(self.ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.put(files = local, remote_path = remote)
            print("---------------------------------------------------\n")
            print("File Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            response = self.SendCommand("ls -l " + remote)
            if response == "":
                print("Remote directory not found") 
            else:
                os.system('dir ' + local)   #See if the local file exists
            print("SCP Transfer Fail") 
            complete = 1
        return(complete)

        #%% SCP communications to get appropriate files from collector
    def getSCP(self, local, remote):
        complete = 0
    
        try:
            scp = SCPClient(self.ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.get(remote_path = remote, local_path = local)
            print("---------------------------------------------------\n")
            print("File Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            response = self.SendCommand("ls -l " + remote)
            if response == "":
                print("Remote file not found") 
            print("SCP Transfer Fail") 
            complete = 1
        return(complete)

    def sendDirectorySCP(self, local, remote):
        complete = 0
    
        try:
            scp = SCPClient(self.ssh.get_transport(), sanitize=lambda x: x) #progress = progress)
            scp.put(files = local, remote_path = remote, recursive = True)
            print("---------------------------------------------------\n")
            print("Directory Transfered Successfully")
            print("---------------------------------------------------\n")
            complete = 1
        except:
            response = self.SendCommand("ls -l " + remote)
            if response == "":
                print("Remote Directory not found") 
            else:
                os.system('dir ' + local)   #See if the local file exists
            print("SCP Transfer Fail") 
            complete = 1
    
        return(complete)



#archived command. the while loop caused issues with timeouts 
def SendCommand1 (self, command):
    #EnvDict = {"PATH":"/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"}
    response = ""
    try: 
        print(" %s \n" % command)
        # Send the command (non-blocking) (string data in, out, error)
        stdin, stdout, stderr = self.ssh.exec_command(command, timeout= 15)
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
        return