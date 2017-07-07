__author__ = 'Majda Moussa'

import time
from subprocess import *
import subprocess
import os.path
import time
from ctypes import *

ADB_PATH = "adb" #Path to the adb command (it is an Android command existing in the Android SDK).
OUTPUT_FOLDER = "/Users/foromodanielsoromou/Downloads/Mooson/results"
APKS_FOLDER = "/Users/foromodanielsoromou/Downloads/Mooson/apks"
RUNS = 15
device_ip = "132.207.242.49"
#device_ip = "192.168.0.100"
def prepare_test_case(file):
	package = "0"

	
	fileName, fileExtension = os.path.splitext(file)
	fileTestCase = fileName + "-androidTest-unaligned.apk"
	#fileTestCase = fileName + "-androidTest.apk"
	print fileTestCase
	# Use only apk files
	if fileName.endswith("-debug") and fileExtension == '.apk':

		package = subprocess.check_output(['./getPackageName.sh', APKS_FOLDER + '/' + file], universal_newlines=True).strip()
		activity = subprocess.check_output(['./getMainActivity.sh', APKS_FOLDER + '/' + file], universal_newlines=True).strip()
		print(package)
		print(activity)
		# The brightness is set to the min value (max value is 255)
		subprocess.call(ADB_PATH + " shell settings put system screen_brightness 0", shell=True, universal_newlines=True)

		# Install the debug application
		print("Installing app " + file + " ...")
		installOutput = check_output(ADB_PATH + " install " + APKS_FOLDER+ '/' + file, shell=True, universal_newlines=True)
	        print("OUTPUT: " + installOutput)

		# Install the apk containing testing case
		print("Installing app containing test case ...")
		installOutput = check_output(ADB_PATH + " install " + APKS_FOLDER + '/' + fileTestCase, shell=True,
                                             universal_newlines=True)
		print("OUTPUT: " + installOutput)
		
	return package


def reset_device(robotiumOutput,package):
    # Check if the test case failed during the testing
    if robotiumOutput.find("FAILURES") > 0:
       print("WARNING: The test case for package '" + package + "' failed.")
       errorsInTestCase.append(fileName + str(iteration+1))
       print()

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
    uninstallOutput = check_output(ADB_PATH + " uninstall " + package + ".test", shell=True,universal_newlines=True)
    print("OUTPUT: " + uninstallOutput)
    # The screen is now off
    subprocess.call(ADB_PATH + " shell svc power stayon false", shell=True)

    # The brightness is set to the medium value
    subprocess.call(ADB_PATH + " shell settings put system screen_brightness 255", shell=True)
 


 	
	


