#!/usr/bin/python
import socket
import os
import time
from Printer.Adafruit_Thermal import *

while True:
        printer = Adafruit_Thermal('/dev/ttyAMA0', 19200, timeout=5)
        pid = os.getpid()
        try:
                ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close($
        except:
                ip = 'NO INTERFACES UP'
        output = '[%s] %s' % (pid, ip)
        print output
        printer.wake()
        printer.setDefault()
        printer.println(output)
        printer.setDefault()
        printer.sleep()
        time.sleep(10)
