import SSH_Comms
import os
import time
cwd = dir_path = os.path.dirname(os.path.realpath(__file__))


class Collector():
    def __init__(self):
        self.CollectorIp = Host #('215.16.144.81')
        #self.CollectorIp = ('10.0.0.96')
        self.LocalPath = ("%s%s") % (cwd, '\\TestOutputV2\\')
        self.LocalFile1 = ("%s%s") % (cwd,'\\egress_testing.sh')
        self.LocalFile2 = ("%s%s") % (cwd,'\\SMART_Tool_Sample_armabihf')
        self.LocalFile3 = ("%s%s") % (cwd,'\\eco-feature-extract-serial-write')
        self.LocalFile4 = ("%s%s") % (cwd, '\\ConfigFix.sh')
        self.RemotePath = '/home/root/'
        self.RemotePath2 = '/'
        self.RemoteFile = '/home/root/N9C350B021801*'
    def SendFile(self): 
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile1, self.RemotePath)
        SSH_Comms.SSH().sendSCP(self.LocalFile2, self.RemotePath)
        SSH_Comms.SSH().SendCommand("tr -d '\r' <egress_testing.sh >egress_testing.sh.new && mv egress_testing.sh.new egress_testing.sh")
        SSH_Comms.SSH().SendCommand('chmod 755 egress_testing.sh')
        SSH_Comms.SSH().SendCommand('chmod 777 SMART_Tool_Sample_armabihf')
        
        SSH_Comms.ssh.close()
        return;
    def GetData(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().getSCP(self.LocalPath, self.RemoteFile)
        SSH_Comms.SSH().SendCommand("rm egress*")
        SSH_Comms.SSH().SendCommand("rm N9C350B0218*")
    def ShutDown(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().SendCommand("./mcu-disable-always-on.sh")
        SSH_Comms.SSH().SendCommand("sync; shutdown -P -t now")
    def SerialFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile3, self.RemotePath2)
        SSH_Comms.SSH().SendCommand("chmod 777 /eco-feature-extract-serial-write")
        SSH_Comms.SSH().SendCommand("/eco-feature-extract-serial-write -s $HOSTNAME")
        SSH_Comms.SSH().SendCommand("rm /eco-feature-ectract-serial-write")
    def ConfigFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile4, self.RemotePath)
        SSH_Comms.SSH().SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("chmod 755 /home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("/home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("rm /home/root/ConfigFix.sh")




#HostNames = ['10.0.0.96']
HostNames = [
'215.16.144.144',
'215.16.144.145',
'215.16.144.146',
]


        

# Main loop, Depending on user input the scrip will either send or recieve a egress testing file. 
print("Select Action \n 1. Send Egress.sh to collector \n 2. Recieve test output from collector \n 3. Shutdown Collector \n 4. Fix the serial number in EEPROM \n 5. Fix the config.ini and config.ini.default")        
TransferType = int(input())    
if TransferType == 1:
    print("Sending Files to Collector Now......")
    for Host in HostNames:
        Collector().SendFile()
elif TransferType == 2:
    for Host in HostNames:
        print("Recieving Files from Collector Now.....")
        Collector().GetData()
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
