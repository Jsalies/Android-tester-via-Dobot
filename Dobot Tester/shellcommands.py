# -*- coding: utf-8 -*-
import subprocess

def SizeScreen():
    '''on recupere la taille de l'ecran en pixels'''
    size = str(subprocess.check_output(".\platform-tools\\adb shell wm size")).replace("\\n", "").split("x")
    width=size[0].split(" ")[-1]
    height=size[1][:4]
    return [height,width]

def Screenshot():
    """ on considère qu'un unique telephone est branché et correctement reconnu (bon drivers)"""
    subprocess.check_output(".\platform-tools\\adb shell screencap sdcard/screen.png")
    subprocess.check_output(".\platform-tools\\adb pull sdcard/screen.png tempo/")


def TempCPU():
    """on recupere la temperature du CPU"""
    temp = subprocess.check_output(".\platform-tools\\adb shell cat /sys/devices/virtual/thermal/thermal_zone0/temp")
    return str(temp).replace("\\r","").replace("\\n","").replace("b","").replace("'","")

def FreqCPU():
    """On recupère la frequence du CPU"""
    freq = subprocess.check_output(".\platform-tools\\adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    return str(freq).replace("\\r", "").replace("\\n", "").replace("b", "").replace("'", "")


def installApk(apkName):
    """On installe l'apk concernée"""
    return subprocess.check_output(".\platform-tools\\adb install " + "\"" + apkName + "\"", shell=True,
                                   universal_newlines=True)


def uninstallApk(apkName):
    """On désinstalle l'apk concernée"""
    return subprocess.check_output(".\platform-tools\\adb uninstall " + apkName, shell=True, universal_newlines=True)


def startApk(apkName, packageName):
    """
    apkname sans le apk
    :param apkName:
    :return:
    """
    subprocess.check_output(".\platform-tools\\adb shell am start -n " + apkName + "/" + packageName)


def closeApk(apkName):
    """
    apkname sans le apk
    :param apkName:
    :return:
    """
    subprocess.check_output(".\platform-tools\\adb shell am force-stop " + apkName)
