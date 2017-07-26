# -*- coding: utf-8 -*-

import os
import platform
from threading import Thread

import DobotDllType as dType
import Dobotfunctions as Dfonct
import OscilloscopeEnergyCollector as OEC
import robot
import screen
import shellcommands as adb
import time

if platform.system()!="Windows":
    import MesureMonsoon as MM

class Simulation(Thread):

    def __init__(self,interface):
        Thread.__init__(self)        
        self.fenetre=interface
        self.fenetre.setpourcent(0)
        self.largueur=interface.Longueur.get()
        self.longueur=interface.Hauteur.get()
        self.repetition=interface.Nbscenar.get()
        self.choixOscillo=interface.ChoixOscillo.get()
        self.tousScenarios=interface.tousScenarios.get()
        self.valeurfrequence=interface.valeurfrequence.get()
        self.powertran=interface.PowerTran.get()
        if self.tousScenarios==0:
            self.scenar=interface.liste.get(interface.liste.curselection())
        
    def run(self):
        """Code à exécuter pendant l'exécution du thread."""  
        #Creation de la pile d'actions du robot        
        api = dType.load()
        #Connect Dobot
        state = dType.ConnectDobot(api, "", 115200)[0]
        
        #si le robot est dans le bon etat
        if (state == dType.DobotConnect.DobotConnect_NotFound):
            self.fenetre.setInstruction("Veuillez brancher le Dobot Magician ou installez les\ndrivers correspondants.")
            return
            
        elif (state == dType.DobotConnect.DobotConnect_Occupied):
            self.fenetre.setInstruction("Veuillez libérer le port USB du robot et Réessayer.")
            return
            
        else:
            self.fenetre.setInstruction("Dobot Magician bien connecté. Démarrage du test.")
            #on initialise le robot
            Dfonct.SpeedInit(api)
            Dfonct.Init(api)
            #on demande au robot la valeur minimum de Z
            Z_min=Dfonct.Calc_Z_Min(api,self.fenetre)
            #on entre les données de notre écran
            ecran=screen.screen(api,self.largueur,self.longueur,self.fenetre)
            #on regarde si nous faisons le test sur un ou plusieurs scénarios
            Filelist=[]
            if self.tousScenarios==1:
                 for fichier in sorted(os.listdir('scenarios/')):
                     Filelist.append(fichier)
            else:
                Filelist.append(self.scenar)
            #on compte le nombre de ligne de tous les scénarios que l'on va utiliser(pour la barre de chargement)
            pas = 0
            for fichier in Filelist:
                lecture = open('scenarios/' + fichier, 'r')
                for ligne in lecture:
                    pas += 1
                pas-=1 # pour la premiere ligne qui represente le package et la derniere qui est toujours vide
            pas=100./float(pas*self.repetition)
            # pour informer l'utilisateur
            self.fenetre.setInstruction("Démarrage de l'oscilloscope.")
            #on lance la mesure d'energie dans l'oscilloscope
            if int(self.choixOscillo) == 2:
                if platform.system() != "Windows":
                    Mesure=MM.Monsoon()
                else:
                    self.fenetre.setInstruction("Le Monsoon n'est actuellement pas supporté par Windows")
                    return
            else:
                Mesure=OEC.OscilloscopeEnergyCollector(self.valeurfrequence,self.fenetre)
            #on test le nombre de scénarios souhaités
            for scenars in Filelist:
                #ouvrir le scénarios
                File=open("./scenarios/"+scenars,'r')
                #récuperer nom de l'apk
                apk=scenars[0:-4]
                #recuperer le package pour le focus
                package=(File.readline()).strip('\n')               
                #récuperer le language pour le robot
                lignecourante=File.readline()
                language=""
                while len(lignecourante)!=0:
                    language+=lignecourante
                    lignecourante=File.readline()
                #fermer le fichier
                File.close
                #on recupere le chemin absolu de l'apk
                try:
                    chemin=os.path.abspath("./apk/"+apk+".apk")
                except:
                    self.fenetre.setInstruction("l'apk spécifié en ligne 1 dans le dossier scénario \nn'est pas présent dans le dossier apk. \nVeuillez l'ajouter ou modifier son nom.")
                    return
                if self.powertran==1:
                    self.fenetre.setInstruction("installation de l'apk PowerTran...")
                    adb.installApk("./ressources/powertran/powertran.apk")
                self.fenetre.setInstruction("installation de l'apk...")
                adb.installApk(chemin)
                self.fenetre.setInstruction("test de l'application")
                # On demarre le test de l'application
                for i in range(1,int(self.repetition)+1):
                    # on tient au courant l'utilisateur
                    self.fenetre.setInstruction("etape "+str(i)+"/"+str(int(self.repetition))+" : En cours")
                    if self.powertran == 1:
                        adb.startApk("powertran", "powertran.start")
                        robot.Robot(api, ecran, self.fenetre, Z_min,"./ressources/powertran/powertran_scenario.sim",0 ).action()
                        adb.closeApk("powertran")
                    # on recupere la temperature et frequence du processeur avant test
                    temp1=adb.TempCPU()
                    freq1=adb.FreqCPU()
                    # on force la luminosité au minimum pour l'homogeneïté des tests
                    adb.Luminosity(0)
                    # on place le robot en position (pour toujours commencer au même endroit)
                    robot.Robot(api, ecran, self.fenetre, Z_min, "mov("+str(int(ecran.pixelwidth)/2)+","+str(int(ecran.pixelheight)/2)+")", 0).action()
                    # On démarre l'oscilloscope sélectionné
                    Mesure.start("./results/"+apk+"-"+str(i)+".csv")
                    #on démarre l'application
                    adb.startApk(apk,package)
                    # temps de pause par sécurité
                    time.sleep(1)
                    # On execute notre scénario complet
                    robot.Robot(api,ecran,self.fenetre,Z_min,language,pas).action()
                    # On ferme l'application
                    adb.closeApk(apk)
                    # On tient au courant l'utilisateur
                    self.fenetre.setInstruction("etape " + str(i) + "/" + str(int(self.repetition)) + " : Enregistrement")
                    # On arete et sauvegarde la mesure d'energie
                    Mesure.stop(True,temp1,freq1,adb.TempCPU(),adb.FreqCPU())
                #Si on utilise la methode powertran
                if self.powertran == 1:
                    self.fenetre.setInstruction("désinstallation de l'apk PowerTran...")
                    adb.uninstallApk("powertran")
                # On tient au courant l'utilisateur
                self.fenetre.setInstruction("désinstallation de l'apk...")
                # Une fois que tout est fait, on désinstalle l'application
                adb.uninstallApk(apk)
        # On tient au courant l'utilisateur
        self.fenetre.setInstruction("Les mesures ont été enregistrées dans\nle dossier results.")
        #on deconnecte le robot
        dType.DisconnectDobot(api)