import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
import os
import threading
import time
from queue import Queue
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
        #self.CollectorIp = Host
        self.LocalPath1 = (cwd + "\\Test_result_logs")#, '\Test_result_logs\\')
        self.LocalPath2 = (cwd + "\\Signature Folders\\" + CurrentVersion + "\\signatures")
        self.LocalPath3 = (cwd + "\\SDTest_result_logs")
        self.LocalFile1 = ("%s%s") % (cwd,'\\eco-feature-extract-serial-write')
        self.LocalFile2 = ("%s%s") % (cwd, '\\Collector_Files\\ConfigFix.sh')
        self.TestFile = ("%s%s") % (cwd,'\\EgressTestV2.py')

        self.RemotePath1 = '/home/root/test'
        self.RemotePath2 = '/'
        self.RemoteFile1 = '/home/root/test/N9C350B021801*' + str(TIMESTAMP) + '*'
    def SendFile(self, ip): 
        SSH_Comms.SSH().Connect(ip)#(self.CollectorIp)
        ### Check for logging directory ###
        DirTest = SSH_Comms.SSH().SendCommand("ls -l /home/root/ | grep test | awk '{printf $9}'")
        if  "test" not in DirTest: 
            SSH_Comms.SSH().SendCommand("mkdir /home/root/test; mkdir /home/root/test/mem; mkdir /home/root/test/sdcard; mkdir /home/root/test/calibration")
            print("'Test' directory did not exist, it has now been created in the /home/root path")
            SSH_Comms.ssh.close()
            time.sleep(1)
            self.SendFile(ip)
        elif "test" in DirTest:
            print("All logging folders already exist, proceeding to deploy test")

        ### Send and Commence Testing ###
        
            SSH_Comms.SSH().sendSCP(self.TestFile, self.RemotePath1)
            SSH_Comms.SSH().sendDirectorySCP(self.LocalPath2, self.RemotePath1)
            SSH_Comms.SSH().SendCommand("PATH=/usr/bin:/usr/local/bin:/sbin:/bin:/usr/sbin && python /home/root/test/EgressTestV2.py")
            print("Completed EgessTestV2")
            SSH_Comms.ssh.close()
            return
    def GetSDhealth(self): 
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().SendCommand('/home/root/bin/SMART_Tool_Sample_armabihf /dev/mmcblk0 > $HOSTNAME.txt')
        SSH_Comms.ssh.close()

    def GetFile(self, ip):
        SSH_Comms.SSH().Connect(ip)#(self.CollectorIp)
        SSH_Comms.SSH().getSCP(self.LocalPath1, self.RemoteFile1)
        SSH_Comms.ssh.close()
    def ShutDown(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().SendCommand("./mcu-disable-always-on.sh")
        SSH_Comms.SSH().SendCommand("sync; shutdown -P -t now")
        SSH_Comms.ssh.close()
    def SerialFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile1, self.RemotePath2)
        SSH_Comms.SSH().SendCommand("chmod 777 /eco-feature-extract-serial-write")
        SSH_Comms.SSH().SendCommand("/eco-feature-extract-serial-write -s $HOSTNAME")
        SSH_Comms.SSH().SendCommand("rm /eco-feature-ectract-serial-write")
        SSH_Comms.ssh.close()
    def ConfigFix(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().sendSCP(self.LocalFile2, self.RemotePath1)
        SSH_Comms.SSH().SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("chmod 755 /home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("/home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("rm /home/root/ConfigFix.sh")
        SSH_Comms.ssh.close()
    def UptimeCheck(self):
        SSH_Comms.SSH().Connect(self.CollectorIp)
        SSH_Comms.SSH().SendCommand("tr -d '\r' <ConfigFix.sh >ConfigFix.sh.new && mv ConfigFix.sh.new ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("chmod 755 /home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("/home/root/ConfigFix.sh")
        SSH_Comms.SSH().SendCommand("rm /home/root/ConfigFix.sh")
        SSH_Comms.ssh.close()

class IpScanner():
    def __init__(self):
        self.q=Queue()
        self.network = ("215.16.144.") #("10.0.0.")
        self.lst = []
    def scanner(self, ip):
        address = self.network + str(ip)
        command = "ping -n 1 " + address 
        #print(command)
        response = os.popen(command)
        if "TTL" in response.read():
            self.lst.append(address)
            print(address + " is live")
            return

    def threader(self):
        while True:
            worker = self.q.get()
            self.scanner(worker)
            self.q.task_done()
    def main(self):
        self.lst = []
        print_lock = threading.Lock()
        startTime = time.time()

        for x in range(100):
            t = threading.Thread(target = self.threader)
            t.daemon = True
            t.start()

        for worker in range(1, 255):
            self.q.put(worker)

        self.q.join()
        print(self.lst)
        print('Scan finished!  -  Time taken:', time.time() - startTime)
        return self.lst


class windowOne():
    def __init__(self, master):
        self.master = master # window
        self.scan = IpScanner()
        self.egress = Collector()
        master.title("Egress Testing App")
        master.geometry('700x400')

        self.button1 = tk.Button(master,text='Scan IP for connected Collectors', command=self.ipscan)
        self.button1.grid(column=2,row=0)

        self.button2 = tk.Button(master,text='Send egress test to selected Collector', command=self.clicked)
        self.button2.grid(column=2,row=1)

        #self.entry1 = tk.Entry(master,width = 10)
        #self.entry1.grid(column=1,row=0)

        #self.label1 = tk.Label(master, text="Input IP range to scan if blank default = 215.16.144.")
        #self.label1.grid(column=0,row=0)
        
        self.label2 = tk.Label(master, text="Scanned Collector IP's")
        self.label2.grid(column=0,row=1)

        self.combo1 = tk.ttk.Combobox(master); self.combo1['values']= ["nothing"]
        self.combo1.grid(column=1,row=1)


    def clicked(self):
        ip = self.combo1.get()
        self.egress.SendFile(ip)
        print(" All tests are now complete, after 20 Seconds all result files will be pulled")
        time.sleep(20)
        self.egress.GetFile(ip)    # Collector().GetFile()
        #messagebox.showinfo('This is a popup', str(value))

    def ipscan(self):
        address = self.scan.main()
        self.combo1["values"] = ['']
        self.combo1["values"] = address#['fdqwd', 'qwdqwwd']


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = windowOne(root)
    root.mainloop()
