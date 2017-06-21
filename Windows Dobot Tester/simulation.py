# -*- coding: utf-8 -*-

from threading import Thread
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen
import robot

class Simulation(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self,fenetre,largueur,longueur,repetition,scenar):
        Thread.__init__(self)
        self.fenetre=fenetre
        self.largueur=largueur
        self.longueur=longueur
        self.repetition=repetition
        self.scenar=scenar
        
    def run(self):
        """Code à exécuter pendant l'exécution du thread."""  
        #Creation de la pile d'actions du robot        
        api = dType.load()
        #Connect Dobot
        state = dType.ConnectDobot(api, "", 115200)[0]
        
        #if the robot has the well state
        if (state == dType.DobotConnect.DobotConnect_NotFound):
            self.fenetre.setInstruction("Veuillez brancher le Dobot Magician ou installez les\ndrivers correspondants.")
            return
            
        elif (state == dType.DobotConnect.DobotConnect_Occupied):
            self.fenetre.setInstruction("Veuillez libérer le port USB du robot et Réessayer.")
            return
            
        else:
            self.fenetre.setInstruction("Dobot Magician bien connecté. Démarrage du test.")
            #ouvrir le scénarios
            File=open("./scenarios/"+self.scenar,'r')
            #récuperer nom de l'apk
            apk=File.readline()                
            #récuperer le language pour le robot
            lignecourante=File.readline()
            language=""
            while len(lignecourante)!=0:
                language+=lignecourante
                lignecourante=File.readline()
            #fermer le fichier
            File.close
            #on initialise le robot
            Dfonct.Init(api)
            #on demande au robot la valeur minimum de Z
            Z_min=Dfonct.Calc_Z_Min(api,self.fenetre)
            #on entre les données de notre écran
            ecran=screen.screen(api,self.largueur,self.longueur,self.fenetre)
            
            #---------------------------------------------
            # DEMARRER MESURE
            #---------------------------------------------
            
            for i in range(1,int(self.repetition)+1):
                #---------------------------------------------
                # INSTALLER APK
                #---------------------------------------------
                robot.robot(api,ecran,Z_min,language)
                #---------------------------------------------
                # DESINSTALLER APK
                #---------------------------------------------
                self.fenetre.setpourcent(float(i)/float(self.repetition)*100.)
            
            self.fenetre.setpourcent(100)
            #---------------------------------------------
            # ARRETER MESURE
            #---------------------------------------------
            
            #---------------------------------------------
            # RECUPERER MESURE
            mesure=1
            #---------------------------------------------
            
            self.fenetre.setMesureEnergie("la consommation total du telephone est de {}Watts\n pour {} tests.\nSoit {}Watts par tests.".format(mesure,self.repetition,float(mesure)/float(self.repetition)))

    def installApk(apkName):
        return subprocess.check_output("adb install " + apkName , shell=True, universal_newlines=True)

    def uninstallApk(apkName):
        return subprocess.check_output("adb uninstall " + apkName , shell=True,universal_newlines=True)

        
