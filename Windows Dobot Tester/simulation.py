# -*- coding: utf-8 -*-

from threading import Thread
import DobotDllType as dType
import Dobotfunctions as Dfonct
import screen
import robot
import subprocess
import os
import OscilloscopeEnergyCollector as OEC
import csv

class Simulation(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self,interface):
        Thread.__init__(self)        
        self.fenetre=interface
        self.largueur=interface.Longueur.get()
        self.longueur=interface.Hauteur.get()
        self.repetition=interface.Nbscenar.get()
        self.choixOscillo=interface.ChoixOscillo.get()
        self.tousScenarios=interface.tousScenarios.get()
        self.valeurfrequence=interface.valeurfrequence.get()
        if self.tousScenarios==0:
            self.scenar=interface.liste.get(interface.liste.curselection())
        
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
            #on regarde si nous faisons le test sur un ou plusieurs scénarios
            Filelist=[]
            if self.tousScenarios==1:
                 for fichier in os.listdir('scenarios/'):
                     Filelist.append(fichier)
            else:
                Filelist.append(self.scenar)
            # pour informer l'utilisateur
            self.fenetre.setInstruction("Démarrage de l'oscilloscope.")
            #on lance la mesure d'energie dans l'oscilloscope
            if self.choixOscillo==2:
                self.fenetre.setInstruction("Oscilloscope non présent\nou pilote non installé.\nVeuillez régler le problème puis réessayer")
                dType.DisconnectDobot(api)
                return
            else:
                Mesure=OEC.OscilloscopeEnergyCollector(self.valeurfrequence)
            #on test le nombre de scénarios souhaités
            for scenars in Filelist:
                #ouvrir le scénarios
                File=open("./scenarios/"+scenars,'r')
                #récuperer nom de l'apk
                apk=scenars.strip('.')
                #recuperer le package pour le focus
                package=(File.readline()).strip('\n')               
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
                #on recupere le chemin absolu de l'apk
                try:
                    chemin=os.path.abspath("./apk/"+apk+".apk")
                except:
                    self.fenetre.setInstruction("l'apk spécifié en ligne 1 dans le fichier scénario \nn'est pas présent dans le fichier apk. \nVeuillez l'ajouter ou modifier son nom.")
                    return
                self.fenetre.setInstruction("installation de l'apk")
                installApk(chemin)
                self.fenetre.setInstruction("test de l'application")
                Consomme=0                
                for i in range(1,int(self.repetition)+1):
                    Mesure.start("./results/"+apk+str(i)+".csv")
                    startApk(apk,package)
                    robot.Robot(api,ecran,self.fenetre,Z_min,language,valeurligne,float(i-1)/float(self.repetition)*100.).action()
                    closeApk(apk)
                    Mesure.stop()
                    Consomme+=calculCsv("./results/"+apk+str(i)+".csv")
                    self.fenetre.setpourcent(float(i)/float(self.repetition)*100.)
                self.fenetre.setInstruction("desinstallation de l'apk")
                uninstallApk(apk)
                self.fenetre.setpourcent(100)
                self.fenetre.setMesureEnergie("la consommation total du telephone est de {}milliWattheure\n pour {} tests.\nSoit {}milliWattheure par tests.".format(Consomme,self.repetition,float(Consomme)/float(self.repetition)))
        
        #on deconnecte le robot        
        dType.DisconnectDobot(api)
        
def installApk(apkName):
    return subprocess.check_output(".\platform-tools\\adb install " + "\"" + apkName + "\"" , shell=True, universal_newlines=True)

def uninstallApk(apkName):
    return subprocess.check_output(".\platform-tools\\adb uninstall " + apkName , shell=True,universal_newlines=True)

def startApk(apkName,packageName):
    """
    apkname sans le apk
    :param apkName: 
    :return: 
    """
    subprocess.check_output(".\platform-tools\\adb shell am start -n " + apkName +"/"+ packageName)
        
def closeApk(apkName):
    """
    apkname sans le apk
    :param apkName: 
    :return: 
    """
    subprocess.check_output(".\platform-tools\\adb shell am force-stop " + apkName)

def calculAire(temps,valeurs):
    """ on prendra en entrée deux listes de même longueur qui representes les deux colonnes des tableaux excels"""
    aire=0
    for i in range(1,len(temps)):
        aire+=(float(temps[i])-float(temps[i-1]))/2.*(float(valeurs[i])+float(valeurs[i-1]))
    return aire

def calculCsv(filename):
    """ calcul la consommation du smartphone via un jeu de données"""
    fichier = csv.reader(open(filename,"rb"))
    liste=[[],[],[],[],[]]
    for row in fichier:
        liste[0].append(row[0])
        liste[1].append(row[1])
        liste[2].append(row[2])
        liste[3].append(row[3])
        liste[4].append(row[4])
    # valeur en milliwatts
    return calculAire(liste[0][1:-1],liste[3][1:-1])/(float(liste[0][-1]))*((float(liste[0][-1]))*10**(-6))/3600.*1000
        
def Screenshot():
    """ on considère qu'un unique telephone est branché et correctement reconnu (bon drivers)"""
    subprocess.check_output(".\platform-tools\\adb shell screencap sdcard/screen.png")
    subprocess.check_output(".\platform-tools\\adb pull sdcard/screen.png tempo/")