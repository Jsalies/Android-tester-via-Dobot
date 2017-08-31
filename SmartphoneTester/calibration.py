# -*- coding: utf-8 -*-

from threading import Thread
import Dobotfunctions as Dfonct
import DobotDllType as dType
import time


class Calibration(Thread):
    def __init__(self, interface):
        Thread.__init__(self)
        self.fenetre = interface

    def run(self):
        api = dType.load()
        # Connection au  Dobot
        state = dType.ConnectDobot(api, "", 115200)[0]
        # si le robot est dans le bon etat
        if (state == dType.DobotConnect.DobotConnect_NotFound):
            self.fenetre.setInstruction("Veuillez brancher le Dobot Magician ou installez les\ndrivers correspondants.")
            return
        elif (state == dType.DobotConnect.DobotConnect_Occupied):
            self.fenetre.setInstruction("Veuillez libérer le port USB du robot et Réessayer.")
            return
        else:
            self.fenetre.setInstruction("Dobot Magician bien connecté. Démarrage du calibrage.")
            z = Dfonct.PositionAndTexte(api, self.fenetre, "placer le bras à son point le plus bas : ")[-1]
            HG = Dfonct.PositionAndTexte(api, self.fenetre, "placer le bras dans le coin haut gauche : ")
            HD = Dfonct.PositionAndTexte(api, self.fenetre, "placer le bras dans le coin haut droit : ")
            BG = Dfonct.PositionAndTexte(api, self.fenetre, "placer le bras dans le coin bas gauche : ")
            BD = Dfonct.PositionAndTexte(api, self.fenetre, "placer le bras dans le coin bas droit : ")
            self.fenetre.setInstruction("debut du test (appuyer sur une touche pour arrêter).")
            self.fenetre.desactive()
            while (True):
                Dfonct.Movement(api, HG[0], HG[1], z)
                if self.fenetre.entrer == 1:
                    break
                Dfonct.Movement(api, HD[0], HD[1], z)
                if self.fenetre.entrer == 1:
                    break
                Dfonct.Movement(api, BG[0], BG[1], z)
                if self.fenetre.entrer == 1:
                    break
                Dfonct.Movement(api, BD[0], BD[1], z)
                if self.fenetre.entrer == 1:
                    break
            self.fenetre.setInstruction("fin du test.")
