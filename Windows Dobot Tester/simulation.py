# -*- coding: utf-8 -*-

from threading import Thread
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen
import robot
import subprocess
import os

class Simulation(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self,fenetre,largueur,longueur,repetition,scenar,oscillochoisi,toutscenarios):
        Thread.__init__(self)
        self.fenetre=fenetre
        self.largueur=largueur
        self.longueur=longueur
        self.repetition=repetition
        self.scenar=scenar
        self.choixOscillo=oscillochoisi
        self.tousScenarios=toutscenarios
        
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
            #on initialise le robot
            Dfonct.Init(api)
            #on demande au robot la valeur minimum de Z
            Z_min=Dfonct.Calc_Z_Min(api,self.fenetre)
            #on entre les données de notre écran
            ecran=screen.screen(api,self.largueur,self.longueur,self.fenetre)
            # pour informer l'utilisateur
            self.fenetre.setInstruction("Démarrage de la simulation.")
            #ouvrir le scénarios
            File=open("./scenarios/"+self.scenar,'r')
            #récuperer nom de l'apk
            apk=File.readline()                
            #récuperer le language pour le robot
            lignecourante=File.readline()
            language=""
            valeurligne=0
            while len(lignecourante)!=0:
                language+=lignecourante
                valeurligne+=1
                lignecourante=File.readline()
            #on compte la valeur en pourcentage du parcours d'une ligne d'action pour le robot
            valeurligne=1./(float(valeurligne+1)*float(self.repetition))*100.
            #fermer le fichier
            File.close
            #---------------------------------------------
            # DEMARRER MESURE
            #---------------------------------------------
            #on recupere le chemin absolu de l'apk
            try:
                chemin=os.path.abspath("./apk/"+apk)
            except:
                self.fenetre.setInstruction("l'apk spécifié en ligne 1 dans le fichier scénario \nn'est pas présent dans le fichier apk. \nVeuillez l'ajouter ou modifier son nom.")
                return
                
            for i in range(1,int(self.repetition)+1):
                installApk(chemin)
                robot.Robot(api,ecran,self.fenetre,Z_min,language,valeurligne,float(i-1)/float(self.repetition)*100.).action()
                uninstallApk(apk[0:-5])
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
        dType.DisconnectDobot(api)
        
def installApk(apkName):
    return subprocess.check_output("\"C:\Users\Administrateur\AppData\Local\Android\sdk\platform-tools\\adb\" install " + "\"" + apkName + "\"" , shell=True, universal_newlines=True)

def uninstallApk(apkName):
    return subprocess.check_output("C:\Users\Administrateur\AppData\Local\Android\sdk\platform-tools\\adb uninstall " + apkName , shell=True,universal_newlines=True)


def startApk(apkName):
    """
    apkname sans le apk
    :param apkName: 
    :return: 
    """
    subprocess.check_output("C:\Users\Administrateur\AppData\Local\Android\sdk\platform-tools\\adb shell am start -a " + apkName)
        

def closeApk(apkName):
    """
    apkname sans le apk
    :param apkName: 
    :return: 
    """
    subprocess.check_output("C:\Users\Administrateur\AppData\Local\Android\sdk\platform-tools\\adb shell am force-stop " + apkName)