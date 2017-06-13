import threading
import DobotDllType as dType
import Dobotfunctions as Dfonct

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

#Load Dll
api = dType.load()

#Connect Dobot
state = dType.ConnectDobot(api, "", 115200)[0]
print("[Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

if (state == dType.DobotConnect.DobotConnect_NoError):
       Dfonct.Init(api)
       z_min=Dfonct.Calc_Z_Min(api)
       Dfonct.Touch(api,z_min)
       
#       pos1=Dfonct.Position(api)
#       pos2=Dfonct.Position(api)
#       Dfonct.Scroll(api,pos1[0],pos1[1],pos2[0],pos2[1],z_min)
       
       coordinates=Dfonct.Keyboard_Calibration(api,"azertyuiop","qsdfghjkl","wxcvbnm")
       text="hey hey je suis un robot qui joue sur un telephone"
       for i in text:
           indice=Dfonct.index_number_keyboard(i,coordinates)
           Dfonct.Movement(api,coordinates[indice][1],coordinates[indice][2],z_min+30)
           Dfonct.Touch(api,z_min)

#Disconnect Dobot
dType.DisconnectDobot(api)


