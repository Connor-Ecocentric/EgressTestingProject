import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog as fd
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
CurrentVersion = 'v3.50.06.04-sdk-05'


class Collector():

    def __init__(self):
        #self.CollectorIp = Host
        if "sdk-03" in CurrentVersion:
            self.RemoteTest = ('/home/root/test/EgressTest-sdk-03.py')
            self.TestFile = ("%s%s") % (cwd,'\\EgressTest-sdk-03.py')
            self.RemoteFile1 = '/home/root/test/N9C350B021801*' + str(TIMESTAMP) + '*'
        elif "sdk-05" in CurrentVersion:
            self.RemoteTest = ('/home/root/test/EgressTest-sdk-05.py')
            self.TestFile = ("%s%s") % (cwd,'\\EgressTest-sdk-05.py')
            self.RemoteFile1 = '/home/root/test/N9C360B012003*' + str(TIMESTAMP) + '*'
        else:
            print("select correct OS version")

        self.LocalPath2 = (cwd + "\\Signature Folders\\" + CurrentVersion + "\\signatures")
        self.RemotePath1 = '/home/root/test'
        self.RemotePath2 = '/'
        self.sshComms = SSH_Comms.SSH()
    def SendFile(self, CollectorIp): 
        self.sshComms.Connect(CollectorIp)
        ### Check for logging directory ###
        DirTest = self.sshComms.SendCommand("ls -l /home/root/ | grep test | awk '{printf $9}'")
        if  "test" not in DirTest: 
            self.sshComms.SendCommand("mkdir /home/root/test; mkdir /home/root/test/mem; mkdir /home/root/test/sdcard; mkdir /home/root/test/calibration")
            print("'Test' directory did not exist, it has now been created in the /home/root path")
            SSH_Comms.ssh.close()
            time.sleep(1)
            self.SendFile(CollectorIp)
        elif "test" in DirTest:
            print("All logging folders already exist, proceeding to deploy test")

        ### Send and Commence Testing ###
        
            self.sshComms.sendSCP(self.TestFile, self.RemotePath1)
            self.sshComms.sendDirectorySCP(self.LocalPath2, self.RemotePath1)
            self.sshComms.SendCommand("PATH=/usr/bin:/usr/local/bin:/sbin:/bin:/usr/sbin && python " + self.RemoteTest)
            print("Completed EgessTestV2")
            SSH_Comms.ssh.close()
            return

    def GetFile(self,CollectorIp,directory):
        self.sshComms.Connect(CollectorIp)
        self.sshComms.getSCP(directory, self.RemoteFile1)
        SSH_Comms.ssh.close()
    def ShutDown(self,CollectorIp):
        self.sshComms.Connect(CollectorIp)
        self.sshComms.SendCommand("./mcu-disable-always-on.sh")
        self.sshComms.SendCommand("sync; shutdown -P -t now")
        SSH_Comms.ssh.close()


class IpScanner():
    def __init__(self):
        self.q=Queue()
        self.network = ("215.16.144.")
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
        self.directory = ""
        master.title("Egress Testing App")
        master.geometry('1000x500')

        self.button1 = tk.Button(master,text='Start scan', command=self.ipscan)
        self.button1.grid(column=2,row=0)

        self.button2 = tk.Button(master,text='Start test', command=self.clicked)
        self.button2.grid(column=2,row=2)

        self.button3 = tk.Button(master,text='Select directory', command=self.opendirectory)
        self.button3.grid(column=2,row=1)

        self.button3 = tk.Button(master,text='Select file', command=self.openfile)
        self.button3.grid(column=2,row=3)
        #self.entry1 = tk.Entry(master,width = 10)
        #self.entry1.grid(column=1,row=0)

        #self.label1 = tk.Label(master, text="Input IP range to scan if blank default = 215.16.144.")
        #self.label1.grid(column=0,row=0)
        self.label1 = tk.Label(master, text="1. Scan LAN for available collectors")
        self.label1.grid(column=0,row=0)

        self.label2 = tk.Label(master, text="2. Select directory to write result files to")
        self.label2.grid(column=0,row=1)

        self.label3 = tk.Label(master, text="3. Select collector IP to send egress to")
        self.label3.grid(column=0,row=2)

        self.label4 = tk.Label(master, text="4. View result file")
        self.label4.grid(column=0,row=3)

        self.label5 = tk.Label(master, text="Activity monitor")
        self.label5.grid(column=3,row=0)

        self.lstbox1 = tk.Listbox(master, selectmode="multiple", width=20, height=5)
        self.lstbox1.grid(column=1,row=2)

        self.text1 = tk.Text(master, height=10, width=60)
        self.text1.grid(column=3,row=1, rowspan = 10)
        self.text1.insert(tk.END, "Activity log")


    def clicked(self):
        if self.directory == "":
            self.text1.insert(tk.END, "\n You must select a directory first")
        else:
            selection = self.lstbox1.curselection()
            print(selection)
            if not selection:
                self.text1.insert(tk.END, "\n No IP address selected.... nothing to do!")
            else:
                for i in selection:
                    ip = self.lstbox1.get(i)
                    self.text1.insert(tk.END, ("\n" + str(ip) + " Has been selected, starting agress test now!"))
                    self.egress.SendFile(ip)
                    self.master.update()
                self.text1.insert(tk.END, "\n All tests are now complete, after 20 Seconds all result files will be pulled")
                self.master.update()
                time.sleep(20)
                for i in selection:
                    ip = self.lstbox1.get(i)
                    self.egress.GetFile(ip,self.directory)
                self.text1.insert(tk.END, "\n All test files have been received you can now check the results")
                self.text1.yview(tk.END)

    def opendirectory(self):
        name = fd.askdirectory()
        self.directory = name
        self.text1.insert(tk.END, "\n Directory Selected: " + self.directory)


    def openfile(self):
        filename = fd.askopenfilename( initialdir=self.directory, title="select file", filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        if filename != "":
            os.system(r"notepad.exe " + filename)


    def ipscan(self):
        address = self.scan.main()
        self.text1.insert(tk.END, ("\n The below collectors have been found! \n" + str(address)))
        for i in range(len(address)):
            self.lstbox1.insert(tk.END, address[i])
        #self.combo1["values"] = ['']
        #self.combo1["values"] = address#['fdqwd', 'qwdqwwd']


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = windowOne(root)
    root.mainloop()
