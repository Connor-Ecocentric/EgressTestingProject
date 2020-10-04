import os
import threading
import time
from queue import Queue

class IpScanner():
    def __init__(self):
        self.q=Queue()
        self.network = ("10.0.0.")#"215.16.144.")
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

scan = IpScanner()
addressList = scan.main()
print('adasdssad' + str(addressList))