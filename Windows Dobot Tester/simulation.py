# -*- coding: utf-8 -*-

import csv
import os
from threading import Thread

import DobotDllType as dType
import Dobotfunctions as Dfonct
import OscilloscopeEnergyCollector as OEC
import robot
import screen
import shellcommands as adb


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
        
        #si le robot est dans le bon etat
        if (state == dType.DobotConnect.DobotConnect_NotFound):
            self.fenetre.setInstruction("Veuillez brancher le Dobot Magician ou installez les\ndrivers correspondants.")
            return
            
        elif (state == dType.DobotConnect.DobotConnect_Occupied):
            self.fenetre.setInstruction("Veuillez libérer le port USB du robot et Réessayer.")
            return
            
        else:
            self.fenetre.setpourcent(0)
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
                Mesure=OEC.OscilloscopeEnergyCollector(self.valeurfrequence,self.fenetre)
            #on test le nombre de scénarios souhaités
            for scenars in Filelist:
                #on remet à zéro pour chaque application
                self.fenetre.setpourcent(0)
                #ouvrir le scénarios
                File=open("./scenarios/"+scenars,'r')
                #récuperer nom de l'apk
                apk=scenars[0:-4]
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
                adb.installApk(chemin)
                self.fenetre.setInstruction("test de l'application")
                #Consomme=0
                for i in range(1,int(self.repetition)+1):
                    self.fenetre.setInstruction("etape "+str(i)+"/"+str(int(self.repetition))+" : En cours")
                    temp1=adb.TempCPU()
                    freq1=adb.FreqCPU()
                    robot.Robot(api, ecran, self.fenetre, Z_min, "mov("+str(int(ecran.pixelwidth)/2)+","+str(int(ecran.pixelheight)/2)+")", 0,float(i - 1) / float(self.repetition) * 100.).action()
                    Mesure.start("./results/"+apk+str(i)+".csv")
                    adb.startApk(apk,package)
                    robot.Robot(api,ecran,self.fenetre,Z_min,language,valeurligne,float(i-1)/float(self.repetition)*100.).action()
                    adb.closeApk(apk)
                    self.fenetre.setpourcent(float(i)/float(self.repetition)*100.)
                    self.fenetre.setInstruction("etape " + str(i) + "/" + str(int(self.repetition)) + " : Enregistrement")
                    Mesure.stop(True,temp1,freq1,adb.TempCPU(),adb.FreqCPU())
                    #Consomme+=calculCsv("./results/"+apk+str(i)+".csv")
                self.fenetre.setInstruction("desinstallation de l'apk")
                adb.uninstallApk(apk)
                self.fenetre.setpourcent(100)
                #self.fenetre.setMesureEnergie("la consommation total du telephone est de {}milliWattheure\n pour {} tests.\nSoit {}milliWattheure par tests.".format(Consomme,self.repetition,float(Consomme)/float(self.repetition)))
        self.fenetre.setInstruction("Les mesures ont été enregistrées dans\nle fichier results.")
        #on deconnecte le robot        
        dType.DisconnectDobot(api)


def calculAire(temps,valeurs):
    """ on prendra en entrée deux listes de même longueur qui representes les deux colonnes des tableaux excels"""
    aire=0
    for i in range(1,len(temps)):
        aire+=(float(temps[i])-float(temps[i-1]))/2.*(float(valeurs[i])+float(valeurs[i-1]))
    return aire

def calculCsv(filename):
    """ calcul la consommation du smartphone via un jeu de données"""
    fichier = csv.reader(open(filename,"r"))
    list=[[],[]]
    for row in fichier:
        list[0].append(row[0])
        list[1].append(row[1])
    # valeur en milliwatts
    return calculAire(list[0][1:-1],list[1][1:-1])/(float(list[0][-1]))*((float(list[0][-1]))*10**(-6))/3600.*1000