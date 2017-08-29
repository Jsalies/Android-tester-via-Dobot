# -*- coding: utf-8 -*-
import subprocess
import platform
import os


# toutes ces commandes sont destinées à demandé/donner une information au telephone connecté à l'ordinateur via le programme "ADB"

def Connect(ip):
    '''On demarre la connection avec le telephone via le Wi-Fi'''
    if platform.system() == "Windows":
        subprocess.check_output(".\platform-tools\\adb connect " + ip)
    else:
        os.popen("adb connect " + ip)


def SizeScreen():
    '''on recupere la taille de l'ecran en pixels'''
    if platform.system() == "Windows":
        size = str(subprocess.check_output(".\platform-tools\\adb shell wm size")).replace("\\n", "").split("x")
        width = size[0].split(" ")[-1]
        height = size[1][:4]
        return [height, width]
    else:
        size = os.popen('adb shell wm size').read().replace("\n", "").replace("\r", "").split('x')
        width = size[0].split(" ")[-1]
        height = size[1]
        return [height, width]


def Screenshot():
    """ on considère qu'un unique telephone est branché et correctement reconnu (bon drivers)"""
    if platform.system() == "Windows":
        subprocess.check_output(".\platform-tools\\adb shell screencap sdcard/screen.png")
        subprocess.check_output(".\platform-tools\\adb pull sdcard/screen.png tempo/")
    else:
        os.popen("adb shell screencap sdcard/screen.png")
        os.popen("adb pull sdcard/screen.png tempo/")


def TempCPU():
    """on recupere la temperature du CPU"""
    if platform.system() == "Windows":
        temp = subprocess.check_output(
            ".\platform-tools\\adb shell cat /sys/devices/virtual/thermal/thermal_zone0/temp")
        return str(temp).replace("\\r", "").replace("\\n", "").replace("b", "").replace("'", "")
    else:
        temp = os.popen("adb shell cat /sys/devices/virtual/thermal/thermal_zone0/temp").read()
        return float(str(temp).replace("\\r", "").replace("\\n", "").replace("b", "").replace("'", ""))


def FreqCPU():
    """On recupère la frequence du CPU"""
    if platform.system() == "Windows":
        freq = subprocess.check_output(
            ".\platform-tools\\adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
        return str(freq).replace("\\r", "").replace("\\n", "").replace("b", "").replace("'", "")
    else:
        freq = os.popen("adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").read()
        return int(str(freq).replace("\\r", "").replace("\\n", "").replace("b", "").replace("'", ""))


def installApk(apkName):
    """On installe l'apk concernée"""
    if platform.system() == "Windows":
        return subprocess.check_output(".\platform-tools\\adb install " + "\"" + apkName + "\"", shell=True,
                                       universal_newlines=True)
    else:
        return os.popen("adb install " + "\"" + apkName + "\"")


def uninstallApk(apkName):
    """On désinstalle l'apk concernée"""
    if platform.system() == "Windows":
        return subprocess.check_output(".\platform-tools\\adb uninstall " + apkName, shell=True,
                                       universal_newlines=True)
    else:
        return os.popen("adb uninstall " + apkName)


def startApk(apkName, packageName):
    """
	apkname sans le apk
	:param apkName:
	:return:
	"""
    if platform.system() == "Windows":
        subprocess.check_output(".\platform-tools\\adb shell am start -n " + apkName + "/" + packageName)
    else:
        os.popen("adb shell am start -n " + apkName + "/" + packageName)


def closeApk(apkName):
    """
	apkname sans le apk
	:param apkName:
	:return:
	"""
    if platform.system() == "Windows":
        subprocess.check_output(".\platform-tools\\adb shell am force-stop " + apkName)
    else:
        os.popen("adb shell am force-stop " + apkName)


def Luminosity(value):
    """ value between 0 and 255"""
    if platform.system() == "Windows":
        subprocess.check_output(".\platform-tools\\adb shell settings put system screen_brightness " + str(value))
    else:
        os.popen("adb shell settings put system screen_brightness " + str(value))


def RobotiumTest(debug, apk):
    if debug == True:
        debug = ""
    else:
        debug = "-e debug false "
    if platform.system() == "Windows":
        subprocess.check_output(
            ".\platform-tools\\adb shell am instrument " + debug + "-w " + apk + ".test/android.test.InstrumentationTestRunner")
    else:
        os.popen("adb shell am instrument " + debug + "-w " + apk + ".test/android.test.InstrumentationTestRunner")
