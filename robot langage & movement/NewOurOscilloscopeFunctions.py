# OscilloscopeStream.py - for LibTiePie 0.5+
#
# This example performs a stream mode measurement and writes the data to OscilloscopeStream.csv.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import time
import os
import sys
import libtiepie
from printinfo import *


# Try to open an oscilloscope with stream measurement support:
def connectToOscilloscope(hertzs, recordLength, callbackFunctionDataReady, callbackFunctionDataOverflow):
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

def measuringToHeatOscilloscope(scp, seconds):
    # Start power monitor
    scp.start()

    # Time to load the app completely
    time.sleep(seconds)

    # Stop power monitor
    scp.stop()

def saveDataToFileCalculatingPowerUsinguCurrent(filePath, data, time, freq):
    csv_file = open(filePath, 'w+')
    try:
        csv_file.write("Time(usecs),CH1,CH2,Power,Energy" + os.linesep)

        # Write csv file
        period = (1.0 / freq) * 1e6
        block = 0
        numberOfBlocks = int(len(data) / 2)
        print("Ecriture dans le fichier")
        for var in range(numberOfBlocks):
            for element in range(len(data[0])):
                csv_file.write(str(time) + ',')
                time = time + period
                v1 = (data)[block][element]
                v2 = (data)[block + 1][element]
                current = v2
                power = v1 * current
                energy = power * (1.0 / freq)

                csv_file.write(str(v1) + ',')  # voltage in phone (from power supply)
                csv_file.write(str(v2) + ',')  # voltage = current in resistor (using ucurrent)
                csv_file.write(str(power) + ',')  # power on phone
                csv_file.write(str(energy))  # energy on phone
                csv_file.write(os.linesep)
            block = block + 2

    except Exception as e:
        return False
        print('Exception: ' + e.message)
    finally:
    		if csv_file is not None :
        		csv_file.close()
        		return True

def saveDataToFileCalculatingPowerUsingAmplifier(filePath, data, time, freq, resistor, gain):
    csv_file = open(filePath, 'w+')
    try:
        #csv_file.write("Time(usecs),CH1,CH2,Power,Energy" + os.linesep)
        csv_file.write("Time(usecs),Power" + os.linesep)

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

                #csv_file.write(str(v1) + ',')  # voltage in phone (from power supply)
                #csv_file.write(str(v2) + ',')  # voltage in resistor (using amplifier)
                csv_file.write(str(power))  # power on phone
                #csv_file.write(str(energy))  # energy on phone
                csv_file.write(os.linesep)
            block = block + 2
    except Exception as e:
        print('Exception: ' + e.message)
        return False
    finally:
        if csv_file is not None:
            csv_file.close()
            return True
