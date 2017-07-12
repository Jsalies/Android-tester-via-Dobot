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

    def start(self,filepath):
        self.filepath=filepath
        mesure=threading.Thread(target=self.engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE))
        mesure.start()

    def stop(self,temp1,freq1,temp2,freq2):
        samples = self.engine.getSamples()
        # Samples are stored in order, indexed sampleEngine.channels values
        f=open(self.filepath,"w")
        f.write("Beginning Temperature : " + temp1 + "C,Beginning Frequency : " + freq1 + "Hz,Ending Temperature : " + temp2 + "C" + ",Ending Frequency : " + freq2 + "Hz\n")
        f.write("Time(usecs),Power" + "\n")
        for i in range(len(samples[sampleEngine.channels.timeStamp])):
            f.write(str(samples[sampleEngine.channels.timeStamp][i])+","+str(samples[sampleEngine.channels.MainCurrent][i]*4.5/1000.))
        f.close()

#import time
#mon=MesureMonsoon()
#mon.start("bob.csv")
#time.sleep(15)
#mon.stop(1,2,3,4)