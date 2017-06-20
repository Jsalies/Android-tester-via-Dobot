# -*- coding: utf-8 -*-
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen as Screen
import robot as Langage
import sys



CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}


api = dType.load()

#Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("[Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

#if the robot has the well state
if (state == dType.DobotConnect.DobotConnect_NoError):
    # we define our work environnement
    Dfonct.Init(api)
    ecran=Screen.screen(api,1000,1000) 
    z_min=Dfonct.Calc_Z_Min(api)

  
print("Fermeture de la connexion")      
dType.DisconnectDobot(api)


