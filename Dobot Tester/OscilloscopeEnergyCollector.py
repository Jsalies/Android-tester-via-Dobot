# -*- coding: utf-8 -*-
import os
from ctypes import CFUNCTYPE, c_void_p

import time
import libtiepie
import sys
import enregistrement


# The callback function to run when data is ready
CALLBACK_DATA_READY = CFUNCTYPE(None, c_void_p)
# The callback function to run when there is overflow
CALLBACK_DATA_OVERFLOW = CFUNCTYPE(None, c_void_p)

class OscilloscopeEnergyCollector:

    def __init__(self,frequence,fenetre):
        self.fenetre = fenetre
        self.func_data_ready = CALLBACK_DATA_READY(self.myfunction1)
        self.func_data_overflow = CALLBACK_DATA_OVERFLOW(self.myfunction2)
        self.frequency = int(frequence)  # Frequency to be set in the oscilloscope to measure
        self.dataRead = []
        self.USING_UCURRENT_DEVICE = False
        self.TIME_INIT = 0
        self.ouputEnergyFileName = ""
        self.RESISTOR = 0.1  # it is used when we measure using the PCB with the amplifier It is the value of the resistor in Ohms.
        self.GAIN = 10.88  # it is used when we measure using the PCB with the amplifier. It is the GAIN set in the amplifier.
        fenetre.setInstruction("Connection à oscilloscope ...")
        self.scp = self.connectToOscilloscope(self.frequency, 1000, self.func_data_ready, self.func_data_overflow,self.fenetre)
        fenetre.setInstruction("Préchauffage de l'oscilloscope ...")
        self.measuringToHeatOscilloscope(self.scp, 5)
        
    def start(self, ouputEnergyFileName):
        self.ouputEnergyFileName = ouputEnergyFileName
        self.dataRead = []
        self.scp.start()

    def stop(self,value,temp1,freq1,temp2,freq2):

        if self.USING_UCURRENT_DEVICE and value==True:
            enregistrement.Enregistrement(self.ouputEnergyFileName, self.dataRead, temp1, freq1, temp2, freq2, 1, self.TIME_INIT,self.frequency)
        elif value==True:
            enregistrement.Enregistrement(self.ouputEnergyFileName, self.dataRead, temp1, freq1, temp2, freq2, 2,self.TIME_INIT, self.frequency,self.RESISTOR, self.GAIN)
        self.scp.stop()

    def myfunction1(self, parameters):
        global dataRead
        if self.scp.is_data_overflow:
            self.fenetre.setInstruction('Data overflow!')
            sys.exit(-1)
        else:
            d = self.scp.get_data()
            self.dataRead.append(d[0])
            self.dataRead.append(d[1])

    def myfunction2(self, parameters):
        if self.scp.is_data_overflow:
            self.fenetre.setInstruction('Data overflow!')
            sys.exit(-1)

    # Try to open an oscilloscope with stream measurement support:
    def connectToOscilloscope(self, hertzs, recordLength, callbackFunctionDataReady, callbackFunctionDataOverflow,fenetre):
        # Search for devices:
        libtiepie.device_list.update()

        # Try to open an oscilloscope with stream measurement support:
        scp = None
        for item in libtiepie.device_list:
            if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
                scp = item.open_oscilloscope()
                if scp.measure_modes & libtiepie.MM_STREAM:
                    break
                else:
                    scp = None

        if scp:
            try:
                # Set measure mode:
                scp.measure_mode = libtiepie.MM_STREAM

                # Set sample frequency in Hz:
                scp.sample_frequency = hertzs

                # Set record length:
                scp.record_length = recordLength

                # Enable channel 1 to measure it:
                scp.channels[0].enabled = True
                scp.channels[1].enabled = True

                # Set coupling:
                scp.channels[0].coupling = libtiepie.CK_DCV  # DC Volt
                scp.channels[1].coupling = libtiepie.CK_DCV
                scp.set_callback_data_ready(callbackFunctionDataReady, None)
                scp.set_callback_data_overflow(callbackFunctionDataOverflow, None)

                # Set range:
                # scp.channels[0]._set_auto_ranging(True)  #Only supported in block mode
                # scp.channels[1]._set_auto_ranging(True)  #Only supported in block mode
                scp.channels[0].range = 8
                scp.channels[1].range = 8
                scp._set_resolution(16)

                # print_device_info(scp)
                # exit(0)
            except Exception as e:
                fenetre.setInstruction('Exception: ' + e.message)
                sys.exit(1)
        else:
            fenetre.setInstruction('Pas d\'oscilloscope disponible avec un système de flux de mesure!')
            sys.exit(1)

        return scp

    def measuringToHeatOscilloscope(self, scp, seconds):
        # Start power monitor
        scp.start()

        # Time to load the app completely
        time.sleep(seconds)

        # Stop power monitor
        scp.stop()