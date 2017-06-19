# -*- coding: utf-8 -*-
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen as Screen
import robot as Langage
import gflags as flags
import sys

FLAGS = flags.FLAGS
flag = False

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

def main(argv):
    useful_flags =["simulationfile", "screenwidth", "screenheight"]
    if not [f for f in useful_flags if FLAGS.get(f,None) is not None]:
       # print (__doc__.string())
        print (FLAGS.MainModuleHelp())
        return
    
    #Load Dll
    api = dType.load()

    #Connect Dobot
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("[Etat de la connexion / Connect status : {}] \n".format(CON_STR[state]))

    #if the robot has the well state
    if (state == dType.DobotConnect.DobotConnect_NoError):
        # we define our work environnement
        Dfonct.Init(api)
        ecran=Screen.screen(api,int(FLAGS.screenwidth),int(FLAGS.screenheight)) 
        z_min=Dfonct.Calc_Z_Min(api)
    
        # we launch our langage through the robot
        Langage.robot(api,ecran,z_min,str(FLAGS.simulationfile))
  
    print("Fermeture de la connexion")      
    dType.DisconnectDobot(api)

if __name__ == '__main__':
    #define flags here to avoid conflicts with peaple who use us as a library
    flags.DEFINE_string("simulationfile", None, "Simulation file")
    flags.DEFINE_integer("screenwidth", None, "Simulation screen width")
    flags.DEFINE_integer("screenheight", None, "Simulation screen height")
    main(FLAGS(sys.argv))


