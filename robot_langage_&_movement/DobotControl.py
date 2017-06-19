# -*- coding: utf-8 -*-
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen as Screen
import robot as Langage

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

#Load Dll
api = dType.load()

#Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("[Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

# if the robot has the well state
if (state == dType.DobotConnect.DobotConnect_NoError):
    # we define our work environnement
    Dfonct.Init(api)
    largueur=raw_input("veuillez entrer la largueur (en pixels) de l'ecran : ")
    hauteur=raw_input("veuillez entrer la hauteur (en pixels) de l'ecran : ")
    ecran=Screen.screen(api,largueur,hauteur) 
    z_min=Dfonct.Calc_Z_Min(api)
    
    # we launch our langage through the robot
    Langage.robot(api,ecran,z_min,"scenarios/com.apusapps.tools.flashtorch.txt.out")
  
print("Fermeture de la connexion")      
dType.DisconnectDobot(api)


