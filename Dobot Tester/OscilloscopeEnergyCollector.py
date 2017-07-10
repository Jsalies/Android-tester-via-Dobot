# -*- coding: utf-8 -*-
import os
from ctypes import CFUNCTYPE, c_void_p

import time
import libtiepie
import sys


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
            powerTraceGenerated = self.saveDataToFileCalculatingPowerUsinguCurrent(self.ouputEnergyFileName, self.dataRead, self.TIME_INIT, self.frequency,temp1,freq1,temp2,freq2,self.fenetre)
        elif value==True:
            powerTraceGenerated = self.saveDataToFileCalculatingPowerUsingAmplifier(self.ouputEnergyFileName, self.dataRead, self.TIME_INIT, self.frequency,
                                                                               self.RESISTOR, self.GAIN,temp1,freq1,temp2,freq2,self.fenetre)
        if powerTraceGenerated:
            self.fenetre.setInstruction('Fichier de mesures écrit')
        else:
            self.fenetre.setInstruction('Erreur pendant l\'ecriture du fichier')
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

    def saveDataToFileCalculatingPowerUsinguCurrent(self, filePath, data, time, freq,temp1,freq1,temp2,freq2,fenetre):
        csv_file = open(filePath, 'w+')
        try:
            csv_file.write("Beginning Temperature : "  + temp1 + "C,Beginning Frequency : "  + freq1 + "Hz,Ending Temperature : "  + temp2 + "C" + ",Ending Frequency : " + freq2 + "Hz\n")
            csv_file.write("Time(usecs),Power" + "\n")

            # Write csv file
            period = (1.0 / freq) * 1e6
            block = 0
            numberOfBlocks = int(len(data) / 2)
            fenetre.setInstruction("Ecriture dans le fichier")
            for var in range(numberOfBlocks):
                for element in range(len(data[0])):
                    v1 = (data)[block][element]
                    v2 = (data)[block + 1][element]
                    power = v1 * v2
                    csv_file.write(str(time) + "," + str(v1 * v2) + "\n")  # power on phone
                    time = time + period
                    csv_file.flush()
                block = block + 2
            csv_file.close()

        except Exception as e:
            return False
            fenetre.setInstruction('Exception: ' + e.message)
        finally:
            if csv_file is not None:
                csv_file.close()
            return True

    def saveDataToFileCalculatingPowerUsingAmplifier(self, filePath, data, time, freq, resistor, gain,temp1,freq1,temp2,freq2,fenetre):
        csv_file = open(filePath, 'w+')
        try:
            csv_file.write("Beginning Temperature : "  + temp1 + "C,Beginning Frequency : "  + freq1 + "Hz,Ending Temperature : "  + temp2 + "C" + ",Ending Frequency : " + freq2 + "Hz\n")
            csv_file.write("Time(usecs),Power" + "\n")

            # Write csv file
            period = (1.0 / freq) * 1e6
            block = 0
            numberOfBlocks = int(len(data) / 2)
            fenetre.setInstruction("Ecriture dans le fichier")
            for var in range(numberOfBlocks):
                for element in range(len(data[0])):
                    csv_file.write(str(time) + ',')
                    time = time + period
                    v1 = (data)[block][element]
                    v2 = (data)[block + 1][element]
                    voltageDifference = float(v2 / gain)
                    current = voltageDifference / resistor
                    power = v1 * current
                    csv_file.write(str(power)+ "\n")  # power on phone
                    csv_file.flush()
                block = block + 2
            csv_file.close()
        except Exception as e:
            fenetre.setInstruction('Exception: ' + e.message)
            return False
        finally:
            if csv_file is not None:
                csv_file.close()
                return True
