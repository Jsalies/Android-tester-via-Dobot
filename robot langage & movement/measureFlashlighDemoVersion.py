__author__ = 'Ruben Saborido Infantes'

import time
from subprocess import *
import subprocess
import os.path
from NewOurOscilloscopeFunctions import *
from ctypes import *

# The callback function to run when data is ready
CALLBACK_DATA_READY = CFUNCTYPE(None, c_void_p)

def myfunction1(parameters):
    global dataRead

    if scp.is_data_overflow:
        print('Data overflow!')
        sys.exit(-1)
    else:
        d = scp.get_data()
        dataRead.append(d[0])
        dataRead.append(d[1])


func_data_ready = CALLBACK_DATA_READY(myfunction1)

# The callback function to run when there is overflow
CALLBACK_DATA_OVERFLOW = CFUNCTYPE(None, c_void_p)

def myfunction2(parameters):
    if scp.is_data_overflow:
        print('Data overflow!')
        sys.exit(-1)

func_data_overflow = CALLBACK_DATA_OVERFLOW(myfunction2)

# Constants
ADB_PATH = "/home/ruben/Software/android-sdk-linux/platform-tools/adb" #Path to the adb command (it is an Android command existing in the Android SDK).
TOOLS_PATH = "/home/ruben/Software/android-sdk-linux/tools" #Path to the tools folder (it is an existing folder in the Android SDK).
RUNS = 30 #Number of runs of each apk.
TIME_INIT = 0
FREQUENCY = 125000 #Frequency to be set in the oscilloscope to measure
RESISTOR = 0.1 #it is used when we measure using the PCB with the amplifier It is the value of the resistor in Ohms.
GAIN = 10.88 #it is used when we measure using the PCB with the amplifier. It is the GAIN set in the amplifier.
USING_UCURRENT_DEVICE = False #It is used to indicate if measurements are taken using the uCurrent device or the PCB with the amplifier.
APKS_FOLDER = "/home/ruben/Desktop/Music/apks/Flashlight" #Folder containing the apks to run.
OUTPUT_FOLDER = "/home/ruben/Desktop/Music/energy/Flashight" #Folder which will contain the collected power traces.
COLLECT_DATA = True #A boolean variable to specify if energy will be measured or not.
PLAYLIST = False #If the app measured is the Andrea's Playlist App

# Prepare oscilloscope:
if COLLECT_DATA:
    dataRead = []
    print("Connecting to oscilloscope ...")
    scp = connectToOscilloscope(FREQUENCY, 1000, func_data_ready, func_data_overflow)
    print("Measuring during 5 seconds to heat the oscilloscope ...")
    measuringToHeatOscilloscope(scp, 5)

#Contains the name of the test cases which failed
errorsInTestCase = []

# For each run
for iteration in range(0, RUNS):
    appNumber = 0

    # for each apk in the folder
    for file in sorted(os.listdir(APKS_FOLDER)):
    
        # The screen is always on
        subprocess.call(ADB_PATH + " shell svc power stayon true", shell=True)

        if os.path.isfile(APKS_FOLDER + '/' + file):
            fileName, fileExtension = os.path.splitext(file)
            fileTestCase = fileName + "-androidTest.apk"

            # Use only apk files
            if fileName.endswith("-debug") and fileExtension == '.apk':
                appNumber = appNumber + 1
                dataRead = []

                print("ITERATION " + str(iteration + 1) + "/" + str(RUNS) + ", APP number " + str(appNumber))

                package = subprocess.check_output(['./getPackageName.sh', APKS_FOLDER + '/' + file], universal_newlines=True).strip()
                activity = subprocess.check_output(['./getMainActivity.sh', APKS_FOLDER + '/' + file], universal_newlines=True).strip()
                print(package)

                # The brightness is set to the min value (max value is 255)
                subprocess.call(ADB_PATH + " shell settings put system screen_brightness 0", shell=True,
                                universal_newlines=True)

                # Install the debug application
                print("Installing app " + file + " ...")
                installOutput = check_output(ADB_PATH + " install " + APKS_FOLDER+ '/' + file, shell=True, universal_newlines=True)
                print("OUTPUT: " + installOutput)

                # Install the apk containing testing case
                print("Installing app containing test case ...")
                installOutput = check_output(ADB_PATH + " install " + APKS_FOLDER + '/' + fileTestCase, shell=True,
                                             universal_newlines=True)
                print("OUTPUT: " + installOutput)

                if COLLECT_DATA:
                    # Start power monitor
                    scp.start()
                    print("starting to measure energy")

                # Start the test case
                print("Test case runs")
                #robotiumOutput = check_output(
                #   ADB_PATH + " shell am instrument -e class " + str(package) + ".test.scenario -w " + str(
                #       package) + ".test/android.test.InstrumentationTestRunner", shell=True, universal_newlines=True)
                #testCommandLine = ADB_PATH + " shell am instrument -w " + str(package) + ".test/android.test.InstrumentationTestRunner"
                #robotiumOutput = check_output(testCommandLine, shell=True, universal_newlines=True)
                #print("Test status : " + robotiumOutput)
                subprocess.call("python DobotControl.py --simulationfile=" + package + " --screenwidth=" + str(width) + " --screenheight=" + str(height), shell=True, universal_newlines=True)


                # Stop measurements
                if COLLECT_DATA:
                    print()
                    # Stop power monitor
                    scp.stop()
                    print("stopping energy measuring")

                # Check if the test case failed during the testing
                if robotiumOutput.find("FAILURES") > 0:
                    print("WARNING: The test case for package '" + package + "' failed.")
                    errorsInTestCase.append(fileName + str(iteration+1))

                # Stop the test case
                print("Stopping the test case ...")
                call(ADB_PATH + " shell am force-stop " + str(package) + ".test", shell=True, universal_newlines=True)

                # Stop the application
                print("Stopping the app ...")
                call(ADB_PATH + " shell am force-stop " + str(package), shell=True, universal_newlines=True)

                # Clean the test case data
                print("Cleaning cache for test case ...")
                call(ADB_PATH + " shell pm clear " + package + ".test", shell=True)

                # Clean the application data
                print("Cleaning cache for the app ...")
                call(ADB_PATH + " shell pm clear " + package, shell=True)

                # Uninstall the application
                print("Uninstalling the app ...")
                uninstallOutput = check_output(ADB_PATH + " uninstall " + package, shell=True, universal_newlines=True)
                print("OUTPUT: " + uninstallOutput)

                # Uninstall the test case
                print("Uninstalling the test case ...")
                uninstallOutput = check_output(ADB_PATH + " uninstall " + package + ".test", shell=True, universal_newlines=True)
                print("OUTPUT: " + uninstallOutput)

                # Save energy file
                if COLLECT_DATA:
                    print("writting energy file")
                    filePath = OUTPUT_FOLDER + "/" + fileName + '-' + str(iteration + 1) + '.energy'

		    if USING_UCURRENT_DEVICE:
			    powerTraceGenerated = saveDataToFileCalculatingPowerUsinguCurrent(filePath, dataRead, TIME_INIT, FREQUENCY)
		    else:
			    powerTraceGenerated = saveDataToFileCalculatingPowerUsingAmplifier(filePath, dataRead, TIME_INIT, FREQUENCY, RESISTOR,GAIN)
		    
		    if powerTraceGenerated:
			    print('Energy file written')
		    else:
		        print('Error writing energy file')

# The screen is now off
subprocess.call(ADB_PATH + " shell svc power stayon false", shell=True)

# The brightness is set to the medium value
subprocess.call(ADB_PATH + " shell settings put system screen_brightness 255", shell=True)

if COLLECT_DATA:
    # Close oscilloscope:
    del scp

print ("Experiment failed for " + str(len(errorsInTestCase)) + " test cases.")
for elem in errorsInTestCase:
    print (elem)

print("DONE!")
