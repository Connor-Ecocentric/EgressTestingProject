# coding: utf-8
import unittest
import logging
import sys
import os
import subprocess
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "CollectorEgressTest.log"


def Sendcmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True)
        return result;
    except:
        os.system(cmd)
        print cmd, 'doesnt seem to have an output pipe, will send again using os'


def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger
def detect_duplicates(list):
    for i in range(len(list)):
        count = list.count(list[i])
        if count == 1:
            duplicate = False 
        else: 
            duplicate = True
            return duplicate;

class SerialNumTest(unittest.TestCase):
    Host  = Sendcmd('printf $HOSTNAME')
    def testConfigini(self):
        self.assertEqual(Sendcmd("more /media/sdcard/config.ini | grep client_id | awk '{printf $3}'"),self.Host)
    def testConfigbak(self):
        self.assertEqual(Sendcmd("more /home/root/config.bak | grep client_id | awk '{printf $3}'"),self.Host)
    def testEprom(self):
        self.assertEqual(Sendcmd("eco-feature-extract -e | grep Serial | awk '{printf $4}'"),self.Host)
class EEMCTest(unittest.TestCase):
    def testAvailPart(self):
        self.assertEqual(Sendcmd("fdisk -l | grep /dev/mmcblk1p | wc -l | awk {'printf $1'}"),'3')
    def testPartSize(self):
        p1 = Sendcmd("fdisk -l | grep /dev/mmcblk1p1 | awk {'printf $5'}")
        p2 = Sendcmd("fdisk -l | grep /dev/mmcblk1p2 | awk {'printf $5'}")
        self.assertEqual(p1,p2)
    def testBootPart(self):
        self.assertIn('b311h',Sendcmd("stat / | grep Device | awk '{printf $2}'"))
    def testRWSpeed(self):
        self.assertGreater(float(Sendcmd("hdparm -t /dev/mmcblk0 | awk '{printf $11}'")),16)
class VersionTest(unittest.TestCase):
    def testEcoversion(self):
        self.assertEqual(Sendcmd("sha1sum /eco-overlay.tar.gz | awk '{print $1}'"),Sendcmd("sha1sum /run/media/mmcblk1p2/eco-overlay.tar.gz | awk '{print$1}'"))
    def testMCUVersion(self):
        Sendcmd("rm mcu.log; ./microBootloaderVersion.sh; ./microResetOnly.sh")
        self.assertEqual(Sendcmd("more mcu.log | grep 'Application Version:' | awk 'NR==1 {printf $9}'"),'v2.002')
    def testBLVersion(self):
        self.assertIn('v1.04',Sendcmd("more mcu.log | grep 'Bootloader Version :' | awk 'NR==1 {printf $9}'"))
class SDCardTest(unittest.TestCase):
    SDdetail = Sendcmd("df -Th | grep mmcblk0 | grep /dev/mmcblk0p2 | awk '{print $2,$3,$6}'")
    def testAvailPart(self):
        self.assertEqual(Sendcmd("fdisk -l | grep mmcblk0p | wc -l | awk {'printf $1'}"),'3')
    def testUpgrade(self):
        self.assertEqual(self.SDdetail.split()[0],'ext4')
        self.assertIn('12.2',self.SDdetail.split()[1])
        self.assertLess(int(self.SDdetail.split()[2].replace('%', '')),30)
    def testRWspeed(self):
        self.assertGreaterEqual(float(Sendcmd("hdparm -t /dev/mmcblk1 | awk '{printf $11}'")),68)
    def testSDPart(self):
        self.assertIn('b302h',Sendcmd("stat /media/sdcard | grep Device | awk '{printf $2}'"))
    def testConfigSchema(self):
        self.assertEqual(len(Sendcmd("more /media/sdcard/config.ini | grep schema | awk '{printf $3}'")),0)    
        self.assertGreater(len(Sendcmd("more /media/sdcard/config.ini.default | grep schema | awk '{printf $3}'")),0)
    def testEndurance(self):
        average = Sendcmd("./SMART_Tool_Sample_armabihf /dev/mmcblk0 | grep Erase | grep Average | awk '{print $4}'")
        maximum = Sendcmd("./SMART_Tool_Sample_armabihf /dev/mmcblk0 | grep Erase | grep Maximum | awk '{print $4}'")
        log.info("SdCard Average erase count: " + str(average))
        log.info("SdCard Maximum erase count: " + str(maximum))
        self.assertLess(int(average),3500)
        self.assertLess(int(maximum),3500)
    def testOutgoingEmpty(self):
        subdir = ['aggregated_data','config','disag_id_data','feature_data','load_id','mode_id','monitor_mode','trash']
        Sendcmd('rm -R /media/sdcard/outgoing; mkdir /media/sdcard/outgoing')
        for dir in subdir:
            Sendcmd('mkdir /media/sdcard/outgoing/' + str(dir))
            
class VoltageCalTest(unittest.TestCase):
    Sendcmd("eco-feature-extract -e | tee calibration.txt")
    P1gain = int(Sendcmd("more calibration.txt | grep 'port: 01' | awk {'printf $17'}"))
    P2gain = int(Sendcmd("more calibration.txt | grep 'port: 02' | awk {'printf $17'}"))
    P3gain = int(Sendcmd("more calibration.txt | grep 'port: 03' | awk {'printf $17'}"))
    P4gain = int(Sendcmd("more calibration.txt | grep 'port: 04' | awk {'printf $17'}"))
    P5gain = int(Sendcmd("more calibration.txt | grep 'port: 05' | awk {'printf $17'}"))
    P6gain = int(Sendcmd("more calibration.txt | grep 'port: 06' | awk {'printf $17'}"))
    P7gain = int(Sendcmd("more calibration.txt | grep 'port: 07' | awk {'printf $17'}"))
    P8gain = int(Sendcmd("more calibration.txt | grep 'port: 08' | awk {'printf $17'}"))
    P9gain = int(Sendcmd("more calibration.txt | grep 'port: 09' | awk {'printf $17'}"))
    P10gain = int(Sendcmd("more calibration.txt | grep 'port: 10' | awk {'printf $17'}"))
    P11gain = int(Sendcmd("more calibration.txt | grep 'port: 11' | awk {'printf $17'}"))
    P12gain = int(Sendcmd("more calibration.txt | grep 'port: 12' | awk {'printf $17'}"))
    Sendcmd("rm calibration.txt")
    CalibrationValues = [P1gain,P2gain,P3gain,P4gain,P5gain,P6gain,P7gain,P8gain,P9gain,P10gain,P11gain,P12gain]
    def testDuplicateValue(self):
        self.assertFalse(detect_duplicates(self.CalibrationValues)) 
    def testDefaultValue(self):
        DefaultGain = 1*2**20
        for value in self.CalibrationValues:
            log.info(' Testing calibration Value: ' + str(value) + ' Against Default Value: ' + str(DefaultGain))
            self.assertNotEqual(value,DefaultGain)
    def testPythonDefaultGain(self):
        # The below test is to ensure the Voltage channel gain values do not equal the default values of calibrate.py
        GainL1 = int(1.0109740 * 2**20)
        GainL2 = int(1.0098220 * 2**20)
        GainL3 = int(1.0170204 * 2**20)
        self.assertNotEqual(self.P10gain,GainL1)
        self.assertNotEqual(self.P11gain,GainL2)
        self.assertNotEqual(self.P12gain,GainL3)
    #tail -30 /media/sdcard/eco-feature-extract.log | grep RMS | awk '{print $39,$41,$43}'
class PeripheralsTest(unittest.TestCase):
    def testTemperature(self):
        self.assertLess(int(Sendcmd("cat /sys/class/thermal/thermal_zone0/temp")),65000)
    def testRTC(self):
        T1 = Sendcmd("hwclock -r | awk {'print $4'}; sleep 2")
        T2 = Sendcmd("hwclock -r | awk {'print $4'}")
        T1sec = T1.split(':')[2]
        T2sec = T2.split(':')[2]
        self.assertGreater(T2sec,T1sec)
    def testUSB(self):
        self.assertGreater(int(Sendcmd('lsusb | grep Marvell | wc -l')),0)
    def testPCI(self):
        self.assertGreater(int(Sendcmd('lspci | grep Marvell | wc -l')),0)
    def testRam(self):
        used_mem = int(Sendcmd("top -bn1 | grep cached | awk 'FNR == 1 {printf $2}'").replace('K',''))
        avail_mem = int(Sendcmd(" top -bn1 | grep cached | awk 'FNR == 1 {printf $4}'").replace('K',''))
        self.assertGreater((used_mem+avail_mem),3850000)

class WifiTest(unittest.TestCase):
    def testLinkQual(self):
        self.assertGreaterEqual(float(Sendcmd("iwconfig wlan0 | grep 'Link Quality' | awk '{printf $4}'").replace('level=', '')),-70)
        level = float(Sendcmd("iwconfig wlan0 | grep 'Link Quality' | awk '{printf $4}'").replace('level=', ''))
        log.info('wifi strength' + str(level))
class MemTest(unittest.TestCase):
    x = 1+1

TEST_FILE = Sendcmd("printf $HOSTNAME") + "_EgressLog.txt"
a = 10
log = get_logger("EgressLog")
log.debug("this is a test")
log.info(" another test" + str(a))
if __name__ == '__main__': 
   with open(TEST_FILE, "w") as f:
       runner = unittest.TextTestRunner(f)
       unittest.main(testRunner=runner)