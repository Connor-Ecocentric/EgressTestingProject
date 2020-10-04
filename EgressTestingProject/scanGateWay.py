import os
import threading
import time
from queue import Queue

class something():
    def scanner(ip):
        address = network + str(ip)
        command = "ping -n 1 " + address 
        #print(command)
        response = os.popen(command)
        if "TTL" in response.read():
            lst.append(address)
            print(address + " is live")
            return

    def threader():
        while True:
            worker = q.get()
            scanner(worker)
            q.task_done()

    lst = []
    print_lock = threading.Lock()
    network = ("10.0.0.")#"215.16.144.")
    q = Queue()
    startTime = time.time()

    for x in range(100):
        t = threading.Thread(target = threader)
        t.daemon = True
        t.start()

    for worker in range(1, 255):
        q.put(worker)

    q.join()
    print(lst)
    print('Scan finished!  -  Time taken:', time.time() - startTime)

something()


