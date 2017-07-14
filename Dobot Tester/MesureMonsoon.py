# -*- coding: utf-8 -*-
import threading
import Monsoon.LVPM as LVPM
import Monsoon.sampleEngine as sampleEngine

class MesureMonsoon:
    def __init__(self):
        self.Mon = LVPM.Monsoon()
        self.Mon.setup_usb()
        self.Mon.setVout(4.5)
        self.engine = sampleEngine.SampleEngine(self.Mon)
        self.engine.disableCSVOutput()
        self.engine.ConsoleOutput(True)
        print(self.Mon.getSerialNumber())

    def start(self,filepath):
        self.filepath=filepath
        self.engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)

    def stop(self,temp1,freq1,temp2,freq2):
        samples = self.engine.getSamples()
        # Samples are stored in order, indexed sampleEngine.channels values
        f=open(self.filepath,"w")
        f.write("Beginning Temperature : " + temp1 + "C,Beginning Frequency : " + freq1 + "Hz,Ending Temperature : " + temp2 + "C" + ",Ending Frequency : " + freq2 + "Hz\n")
        f.write("Time(usecs),Power" + "\n")
        for i in range(len(samples[sampleEngine.channels.timeStamp])):
            f.write(str(samples[sampleEngine.channels.timeStamp][i])+","+str(samples[sampleEngine.channels.MainCurrent][i]*4.5/1000.))
        f.close()

import usb
busses = usb.busses()
for bus in busses:
  devices = bus.devices
  for dev in devices:
    print (repr(dev))
    print ("Device:", dev.filename)
    print ("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
    print ("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))
    print ("Manufacturer:", dev.iManufacturer)
    print ("Serial:", dev.iSerialNumber)
    print ("Product:", dev.iProduct)



import usb.core
print (usb.core.find(find_all=True))
print (usb.core.show_devices())
import time
mon=MesureMonsoon()
mon.start("bob.csv")
time.sleep(15)
mon.stop(1,2,3,4)