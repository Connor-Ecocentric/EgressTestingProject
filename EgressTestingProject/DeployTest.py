import SSH_Comms
import os
import time
import datetime
now = datetime.datetime.now()
TIMESTAMP = now.strftime("%Y%m%d")
cwd = dir_path = os.path.dirname(os.path.realpath(__file__))
CurrentVersion = 'v3.50.05.11'



class Collector():
    def __init__(self):
        #self.CollectorIp = Host
        self.CollectorIp = Host
        self.LocalPath1 = (cwd + "\\Test_result_logs")#, '\Test_result_logs\\')
        self.LocalPath2 = (cwd + "\\Signature Folders\\" + CurrentVersion + "\\signatures")
        self.LocalPath3 = (cwd + "\\SDTest_result_logs")
        self.LocalFile1 = ("%s%s") % (cwd,'\\eco-feature-extract-serial-write')
        self.LocalFile2 = ("%s%s") % (cwd, '\\Collector_Files\\ConfigFix.sh')
        self.TestFile = ("%s%s") % (cwd,'\\EgressTestV2.py')
        self.RemotePath1 = '/home/root/test'
        self.RemotePath2 = '/'
        self.RemoteFile1 = '/home/root/test/N9C350B021801*' + str(TIMESTAMP) + '*'
        self.sshComms = SSH_Comms.SSH()
    def SendFile(self): 
        self.sshComms.Connect(self.CollectorIp)
        ### Check for logging directory ###
        DirTest = self.sshComms.SendCommand("ls -l /home/root/ | grep test | awk '{printf $9}'")
        if  "test" not in DirTest: 
            self.sshComms.SendCommand("mkdir /home/root/test; mkdir /home/root/test/mem; mkdir /home/root/test/sdcard; mkdir /home/root/test/calibration")
            print("'Test' directory did not exist, it has now been created in the /home/root path")
            SSH_Comms.ssh.close()
            time.sleep(1)
            self.SendFile()
        elif "test" in DirTest:
            print("All logging folders already exist, proceeding to deploy test")

        ### Send and Commence Testing ###
        
            self.sshComms.sendSCP(self.TestFile, self.RemotePath1)
            self.sshComms.sendDirectorySCP(self.LocalPath2, self.RemotePath1)
            self.sshComms.SendCommand("PATH=/usr/bin:/usr/local/bin:/sbin:/bin:/usr/sbin && python /home/root/test/EgressTestV2.py")
            print("Completed EgessTestV2")
            SSH_Comms.ssh.close()
            return
    def GetSDhealth(self): 
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.SendCommand('/home/root/bin/SMART_Tool_Sample_armabihf /dev/mmcblk0 > $HOSTNAME.txt')
        SSH_Comms.ssh.close()

    def GetFile(self):
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.getSCP(self.LocalPath1, self.RemoteFile1)
        SSH_Comms.ssh.close()
    def ShutDown(self):
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.SendCommand("./mcu-disable-always-on.sh")
        self.sshComms.SendCommand("sync; shutdown -P -t now")
        SSH_Comms.ssh.close()
    def SerialFix(self):
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.sendSCP(self.LocalFile1, self.RemotePath2)
        self.sshComms.SendCommand("chmod 777 /eco-feature-extract-serial-write")
        self.sshComms.SendCommand("/eco-feature-extract-serial-write -s $HOSTNAME")
        self.sshComms.SendCommand("rm /eco-feature-ectract-serial-write")
        SSH_Comms.ssh.close()
    def ConfigFix(self):
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.sendSCP(self.LocalFile2, self.RemotePath1)
        self.sshComms.SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        self.sshComms.SendCommand("chmod 755 /home/root/ConfigFix.sh")
        self.sshComms.SendCommand("/home/root/ConfigFix.sh")
        self.sshComms.SendCommand("rm /home/root/ConfigFix.sh")
        SSH_Comms.ssh.close()
    def UptimeCheck(self):
        self.sshComms.Connect(self.CollectorIp)
        self.sshComms.SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        self.sshComms.SendCommand("chmod 755 /home/root/ConfigFix.sh")
        self.sshComms.SendCommand("/home/root/ConfigFix.sh")
        self.sshComms.SendCommand("rm /home/root/ConfigFix.sh")
        SSH_Comms.ssh.close()

def notsure():
    print("Enter Ip of collectors you wish to test as an array. eg. ['10.0.0.69']")
    for attempt in range(10):
        try:
            HostNames = ["215.16.144.58",
            "215.16.144.60",
            "215.16.144.46",
            "215.16.144.52",
            "215.16.144.71",
            "215.16.144.82",
            "215.16.144.91",
            "215.16.144.123"]# input()
        except:
            print('Input incorrect, be sure to follow the suggested structure')
        else:
            break
    else:
        print('FAIL!')

HostNames = [
    '215.16.144.163'
]
# Main loop, Depending on user input the script will either send or recieve a egress testing file. 
print("Select Action \n 1. Send Egress.sh to collector \n 2. Recieve test output from collector \n 3. Shutdown Collector \n 4. Fix the serial number in EEPROM \n 5. Fix the config.ini and config.ini.default \n 6. SDHealth")        
TransferType = int(input())    
if TransferType == 1:
    print("Sending Files to Collector Now......")
    for Host in HostNames:
        Collector().SendFile()
    print(" All tests are now complete, after 20 Seconds all result files will be pulled")
    time.sleep(20)
    for Host in HostNames:
        Collector().GetFile()
    
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
else:
    print("Input a valid number")

