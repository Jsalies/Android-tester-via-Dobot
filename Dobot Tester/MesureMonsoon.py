import monsoon
import threading
import sys
import time
import platform

class Mesure_Monsoon:

    def __init__(self,Volt,Amp,fenetre):
        #pour pouvoir ecrire à l'ecran:
        self.fenetre=fenetre
        #on trouve notre peripherique dans la liste de ceux existants:
        if platform.system() == "Windows":
            device="COM3"
        elif platform.system() == "Linux":
            device="/dev/bus/usb/004/002"
        #on crée notre oscilloscope
        self.mon = monsoon.Monsoon(device)
        #on fix la valeur du voltage
        self.mon.SetVoltage(Volt)
        #on fix la valeur maximum du courant
        self.mon.SetMaxCurrent(Amp)
        #on choisi d'avoir acces au port usb du monsoon via l'ordinateur
        self.mon.SetUsbPassthrough(1)
        #on afiche les parametres du monsoon
        items = sorted(self.mon.GetStatus().items())
        print ("\n".join(["%s: %s" % item for item in items]))
        #on defini notre condition d'arret
        self.continuer=1
        #on lance la collecte de données MAIS PAS LA RECUPERATION /!\
        self.mon.StartDataCollection()
        #on prépare notre thread qui recuperera les mesures
        self.mesure = threading.Thread(target=self.mon.mesure)

    def mesure(self):
        self.fenetre.setInstruction("Démarrage de la collecte")
        #on ouvre le fichier de collecte
        with open (self.filepath, 'a') as fd:
            old_stdout = sys.stdout
            sys.stdout = fd
            print("Beginning Temperature : "  + self.temp1 + "C,Beginning Frequency : "  + self.freq1 + "Hz")
            print("temps,Amperage")
            BeginningTime=time.time()
            #on recupere un échantillons tant que l'on veut
            while (self.continuer==1):
                samples = self.mon.CollectData()
                CurrentTime=time.time()
                print (CurrentTime-BeginningTime,samples)
            #une fois que c'est fini, on arrete la collecte
            self.fenetre.setInstruction("Arrêt de la collecte")
            self.mon.StopDataCollection()

    def start(self,filepath,temp1,freq1):
        self.temp1=temp1
        self.freq1=freq1
        #on conserve le nom du fichier ou l'on écrira nos données
        self.filepath=filepath
        #on lance le thread pour les mesures
        self.mesure.start()

    def stop(self,temp1,freq1):
        self.temp1 = temp1
        self.freq1 = freq1
        self.continuer=0