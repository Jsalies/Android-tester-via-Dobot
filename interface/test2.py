# -*- coding: utf-8 -*-
import random
import sys
from threading import Thread
import time
import classInterface

class Afficheur(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self,fenetre):
        Thread.__init__(self)
        self.fenetre=fenetre
        
    def run(self):
        """Code à exécuter pendant l'exécution du thread."""
        while 1:
            self.fenetre.setInstruction("hey hey")
            attente = 0.2
            attente += random.randint(1, 60) / 100
            time.sleep(attente)