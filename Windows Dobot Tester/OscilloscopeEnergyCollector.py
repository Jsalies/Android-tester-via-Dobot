import os
from ctypes import CFUNCTYPE, c_void_p

import time
import libtiepie
__author__ = 'Foromo Daniel Soromou'
import sys


# The callback function to run when data is ready
CALLBACK_DATA_READY = CFUNCTYPE(None, c_void_p)
# The callback function to run when there is overflow
CALLBACK_DATA_OVERFLOW = CFUNCTYPE(None, c_void_p)

class OscilloscopeEnergyCollector:

    def __init__(self,frequence,fenetre):
        self.func_data_ready = CALLBACK_DATA_READY(self.myfunction1)
        self.func_data_overflow = CALLBACK_DATA_OVERFLOW(self.myfunction2)
        self.frequency = int(frequence)  # Frequency to be set in the oscilloscope to measure
        self.dataRead = []
        self.USING_UCURRENT_DEVICE = True
        self.TIME_INIT = 0
        self.ouputEnergyFileName = ""
        self.RESISTOR = 0.1  # it is used when we measure using the PCB with the amplifier It is the value of the resistor in Ohms.
        self.GAIN = 10.88  # it is used when we measure using the PCB with the amplifier. It is the GAIN set in the amplifier.
        fenetre.setInstruction("Connection à oscilloscope ...")
        self.scp = self.connectToOscilloscope(self.frequency, 1000, self.func_data_ready, self.func_data_overflow)
        fenetre.setInstruction("Préchauffage de l'oscilloscope ...")
        self.measuringToHeatOscilloscope(self.scp, 5)
        
    def start(self, ouputEnergyFileName):
        self.ouputEnergyFileName = ouputEnergyFileName
        self.dataRead = []
        self.scp.start()

    def stop(self,value,temp1,freq1,temps2,freq2):

        if self.USING_UCURRENT_DEVICE and value==True:
            powerTraceGenerated = self.saveDataToFileCalculatingPowerUsinguCurrent(self.ouputEnergyFileName, self.dataRead, self.TIME_INIT, self.frequency,temp1,freq1,temps2,freq2)
        elif value==True:
            powerTraceGenerated = self.saveDataToFileCalculatingPowerUsingAmplifier(self.ouputEnergyFileName, self.dataRead, self.TIME_INIT, self.frequencyf,
                                                                               self.RESISTOR, self.GAIN)
        if powerTraceGenerated:
            print('Energy file written')
        else:
            print('Error writing energy file')
        self.scp.stop()

    def myfunction1(self, parameters):
        global dataRead
        if self.scp.is_data_overflow:
            print('Data overflow!')
            sys.exit(-1)
        else:
            d = self.scp.get_data()
            self.dataRead.append(d[0])
            self.dataRead.append(d[1])

    def myfunction2(self, parameters):
        if self.scp.is_data_overflow:
            print('Data overflow!')
            sys.exit(-1)

    # Try to open an oscilloscope with stream measurement support:
    def connectToOscilloscope(self, hertzs, recordLength, callbackFunctionDataReady, callbackFunctionDataOverflow):
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
                print('Exception: ' + e.message)
                sys.exit(1)
        else:
            print('No oscilloscope available with stream measurement support!')
            sys.exit(1)

        return scp

    def measuringToHeatOscilloscope(self, scp, seconds):
        # Start power monitor
        scp.start()

        # Time to load the app completely
        time.sleep(seconds)

        # Stop power monitor
        scp.stop()

    def saveDataToFileCalculatingPowerUsinguCurrent(self, filePath, data, time, freq,temp1,freq1,temp2,freq2):
        csv_file = open(filePath, 'w+')
        try:
            csv_file.write("Beginning Temperature : "  + temp1 + "°C,Beginning Frequency : "  + freq1 + "Hz,Ending Temperature : "  + temp2 + "°C" + ",Ending Frequency : " + freq2 + "Hz\n")
            csv_file.write("Time(usecs),Power" + "\n")

            # Write csv file
            period = (1.0 / freq) * 1e6
            block = 0
            numberOfBlocks = int(len(data) / 2)
            print("Ecriture dans le fichier")
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
            print('Exception: ' + e.message)
        finally:
            if csv_file is not None:
                csv_file.close()
            return True

    def saveDataToFileCalculatingPowerUsingAmplifier(self, filePath, data, time, freq, resistor, gain):
        csv_file = open(filePath, 'w+')
        try:
            # csv_file.write("Time(usecs),CH1,CH2,Power,Energy" + os.linesep)
            csv_file.write("Time(usecs),Power" + "\n")

            # Write csv file
            period = (1.0 / freq) * 1e6
            block = 0
            numberOfBlocks = int(len(data) / 2)
            for var in range(numberOfBlocks):
                for element in range(len(data[0])):
                    csv_file.write(str(time) + ',')
                    time = time + period
                    v1 = (data)[block][element]
                    v2 = (data)[block + 1][element]
                    voltageDifference = float(v2 / gain)
                    current = voltageDifference / resistor
                    power = v1 * current
                    energy = power * (1.0 / freq)
                    # csv_file.write(str(v1) + ',')  # voltage in phone (from power supply)
                    # csv_file.write(str(v2) + ',')  # voltage in resistor (using amplifier)
                    csv_file.write(str(power)+ "\n")  # power on phone
                    # csv_file.write(str(energy))  # energy on phone
                block = block + 2
        except Exception as e:
            print('Exception: ' + e.message)
            return False
        finally:
            if csv_file is not None:
                csv_file.close()
                return True