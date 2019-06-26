import SSH_Comms
import os
import time
cwd = dir_path = os.path.dirname(os.path.realpath(__file__))
CurrentVersion = 'v3.50.05.11'


class Collector():
    def __init__(self):
        self.CollectorIp = Host
        #self.CollectorIp = ('10.0.0.96')
        self.LocalPath = (cwd + "\\Test_result_logs")#, '\Test_result_logs\\')
        self.LocalPath1 = (cwd + "\\Signature Folders\\" + CurrentVersion + "\\signatures")
        self.LocalPath2 = (cwd + "\\SDTest_result_logs")
        self.TestFile = ("%s%s") % (cwd,'\\EgressTestV2.py')
        self.DependencyFile1 = ("%s%s") % (cwd,'\Collector_Files\\SMART_Tool_Sample_armabihf')
        self.LocalFile3 = ("%s%s") % (cwd,'\\eco-feature-extract-serial-write')
        self.LocalFile4 = ("%s%s") % (cwd, '\\Collector_Files\\ConfigFix.sh')
        self.RemotePath = '/home/root/'
        self.RemotePath2 = '/'
        self.RemoteFile = '/home/root/N9C350B021801*'
    def SendFile(self): 
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.TestFile, self.RemotePath)
        SSH_Comms.SSH().sendSCP(self.DependencyFile1, self.RemotePath)
        SSH_Comms.SSH().sendDirectorySCP(self.LocalPath1, self.RemotePath)
        SSH_Comms.SSH().SendCommand('chmod 777 EgressTestV2.py')
        SSH_Comms.SSH().SendCommand('chmod 777 SMART_Tool_Sample_armabihf')
        SSH_Comms.SSH().SendCommand("PATH=/usr/bin:/usr/local/bin:/sbin:/bin:/usr/sbin && python EgressTestV2.py")
        print("Completed EgessTestV2")
        SSH_Comms.ssh.close()
        return
    def GetSDhealth(self): 
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.DependencyFile1, self.RemotePath)
        SSH_Comms.SSH().SendCommand('chmod 777 SMART_Tool_Sample_armabihf')
        SSH_Comms.SSH().SendCommand('./SMART_Tool_Sample_armabihf /dev/mmcblk0 >> $HOSTNAME.txt')
        SSH_Comms.ssh.close()

    def GetFile(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().getSCP(self.LocalPath, self.RemoteFile)
        print("Completing final cleanup...... deleting log file and SMART tool file")
        SSH_Comms.SSH().SendCommand('rm N9C350B021801*')
        SSH_Comms.SSH().SendCommand('rm SMART_Tool_Sample_armabihf')      
        SSH_Comms.ssh.close()
    def ShutDown(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().SendCommand("./mcu-disable-always-on.sh")
        SSH_Comms.SSH().SendCommand("sync; shutdown -P -t now")
        SSH_Comms.ssh.close()
    def SerialFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile3, self.RemotePath2)
        SSH_Comms.SSH().SendCommand("chmod 777 /eco-feature-extract-serial-write")
        SSH_Comms.SSH().SendCommand("/eco-feature-extract-serial-write -s $HOSTNAME")
        SSH_Comms.SSH().SendCommand("rm /eco-feature-ectract-serial-write")
        SSH_Comms.ssh.close()
    def ConfigFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile4, self.RemotePath)
        SSH_Comms.SSH().SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("chmod 755 /home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("/home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("rm /home/root/ConfigFix.sh")
        SSH_Comms.ssh.close()




HostNames = ['215.16.144.68',
             '215.16.144.50',
             '215.16.144.80',
             '215.16.144.128',]
             



        

# Main loop, Depending on user input the scrip will either send or recieve a egress testing file. 
print("Select Action \n 1. Send Egress.sh to collector \n 2. Recieve test output from collector \n 3. Shutdown Collector \n 4. Fix the serial number in EEPROM \n 5. Fix the config.ini and config.ini.default \n 6. SDHealth")        
TransferType = int(input())    
if TransferType == 1:
    print("Sending Files to Collector Now......")
    for Host in HostNames:
        Collector().SendFile()
       #time.sleep(5)
       #Collector().GetFile()
elif TransferType == 2:
    for Host in HostNames:
        print("Recieving Files from Collector Now.....")
        Collector().GetFile()
elif TransferType == 3:
    for Host in HostNames:
        print("Bye Bye")
        Collector().ShutDown()
elif TransferType == 4:
    for Host in HostNames:
        Collector().SerialFix()
elif TransferType == 5:
    for Host in HostNames:
        Collector().ConfigFix()
elif TransferType == 6:
    for Host in HostNames:
        Collector().GetSDhealth()
        time.sleep(5)
        Collector().GetFile()

