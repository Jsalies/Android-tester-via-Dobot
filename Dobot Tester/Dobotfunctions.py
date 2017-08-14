# -*- coding: utf-8 -*-
import DobotDllType as dType
import time

#--------------------------------------------MOVEMENTS----------------------------------------

def SpeedInit(api):
    """ we precise the arms triggers"""
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued = 1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued = 1)
    dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued = 1)
    # Start to Execute Command Queued
    dType.SetQueuedCmdStartExec(api)
    time.sleep(1)
    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)


def Init(api):
    """ to keep a good accuracy, we calibrate our arm.
    This function must be called before all kind of arm using"""
    #Clean Command Queued
    dType.SetQueuedCmdClear(api)
    #Async Home
    dType.SetHOMECmd(api, temp = 0, isQueued = 1)
    #Useless movement which permit to wait the init end.
    tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 210, 0, 135, 0, isQueued = 1)[0]
    #Start to Execute Command Queued
    dType.SetQueuedCmdStartExec(api)
    #Wait for Executing Last Command
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    #Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    
    
def Calc_Z_Min(api,fenetre):
    """ SECURITE : le bras robotic va attendre que vous
    le placiez à sa valeur la plus basse de z
    SECURITY : the robot will wait that you put
    the robotic arm at is lowest z value"""
    fenetre.setInstruction("""--------------------CALIBRAGE / CALIBRATION--------------------
 placez le robot en position d'appuie / lean the robot on a button
------------puis appuyer sur ENTRER / then press ENTER------------""")
    fenetre.desactive()
    while fenetre.entrer==0:
        {}
    fenetre.desactive()
    a=dType.GetPose(api)
    return a[2]
    
def Position(api,fenetre):
    """ pour recuperer la position du bras / to get the current arm's position"""
    fenetre.setInstruction("""placez le robot en position (puis ENTREZ) / put the robot at the desired position (then ENTER) : \n""")
    fenetre.desactive()
    while fenetre.entrer == 0:
        {}
    pos=dType.GetPose(api)
    return pos
    
def Movement(api,x,y,z):
    """ deplace le bras vers la position (x,y,z)
    move the arm to (x,y,z)"""
    dType.SetQueuedCmdClear(api)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, 0, isQueued = 1)[0]
    tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, 0, isQueued = 1)[0]
    dType.SetQueuedCmdStartExec(api)    
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)
    

def Touch(api,z_min):
    """move the arm to touch a button and back to its initial position"""
    a=dType.GetPose(api)    
    dType.SetQueuedCmdClear(api)
    dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,a[0],a[1],z_min, 0, isQueued = 1)[0]
    tempo=dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,a[0],a[1],z_min+30, 0, isQueued = 1)[0]
    dType.SetQueuedCmdStartExec(api)    
    while tempo > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)

def Scroll(api,x_begin,y_begin,x_end,y_end,z_min):
    """permit to the robot to scroll with a movement from x_begin,y_begin to x_end,y_end"""
    Movement(api,x_begin,y_begin,z_min+30)
    Movement(api,x_begin,y_begin,z_min)
    Movement(api,x_end,y_end,z_min)
    Movement(api,x_end,y_end,z_min+30)