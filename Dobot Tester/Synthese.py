# -*- coding: utf-8 -*-
import os
from threading import Thread
import pandas as pd
import numpy as np


class synthese(Thread):

    def __init__(self,fenetre):
        Thread.__init__(self)
        self.fenetre=fenetre
        self.data_entree = "./results/"
        self.frequency = float(fenetre.frequence.get())
        self.summary = []
        self.measurement_tools="WithRobot"
        self.measurement_mode="WithDebug"
        if fenetre.ChoixOscillo.get()==1:
            self.measurement_system= "HomeSystem"
        else:
            self.measurement_system= "MonsoonSystem"
        if fenetre.PowerTran.get()==0:
            self.measurement_method="WithoutPowertran"
        else:
            self.measurement_method= "WithPowertran"
        if fenetre.choixconnection.get() == 2:
            self.measurement_protocol = "WiFi"
        else:
            self.measurement_protocol = "USB"
        self.data_sortie=self.measurement_tools+"_"+self.measurement_protocol+"_"+self.measurement_mode+"_"+self.measurement_system+"_"+self.measurement_method
        print (self.data_sortie)
    def run(self):
        # On compte le nombre de fichiers à traiter
        self.fenetre.setpourcent(0)
        if len(os.listdir(self.data_entree))==0:
            self.fenetre.setInstruction("le dossier \"./résults\" est vide.")
            return
        pas=100./len(os.listdir(self.data_entree))
        #pour chaque fichier dans./results/
        for file in sorted(os.listdir(self.data_entree)):
            if file.endswith('.csv'):
                self.fenetre.setInstruction("calculs pour : "+file)
                fichier = open(self.data_entree + file, "r")
                fichier.readline()
                tempo = open("tempo.csv", "w")
                for line in fichier:
                    tempo.write(line)
                tempo.close()
                #on ouvre notre csv
                data = pd.read_csv("tempo.csv")['Power']
                # on calculs toutes les valeurs pertinentes
                dmin = np.amin(data)
                dmax = np.amax(data)
                mean = np.mean(data)
                stdev = np.std(data)
                median = np.median(data)
                sum_square = np.sum(data ** 2)
                sum_square_divided_by_frequency = np.sum((data ** 2) /float(self.frequency))
                percentile_25 = np.percentile(data, 25)
                percentile_50 = np.percentile(data, 50)
                percentile_75 = np.percentile(data, 75)
                number_of_samples = len(data)

                self.summary.append({
                    'name': file[:file.rfind('-')],
                    'id': file[file.rfind('-')+1:file.rfind('.')],
                    'category': "\(O_O)/",
                    'measurement_tools': self.measurement_tools,
                    'measurement_mode': self.measurement_mode,
                    'measurement_system': self.measurement_system,
                    'measurement_method': self.measurement_method,
                    'measurement_protocol': self.measurement_protocol,
                    'min_value': dmin, 'number_of_samples': number_of_samples,
                    'max_value': dmax, 'mean': mean, 'stdev': stdev,
                    'median_value': median, 'sum_square': sum_square,
                    'sum_square/frequency': sum_square_divided_by_frequency,
                    'percentile_25': percentile_25,
                    'percentile_50': percentile_50,
                    'percentile_75': percentile_75})

                self.fenetre.setpourcent(self.fenetre.getpourcent()+pas)

        os.remove("tempo.csv")
        sorted(self.summary, key=lambda k: (k['name'], k['id']))
        summary = pd.DataFrame(self.summary, columns=['name', 'id', 'number_of_samples','category',
                    'measurement_tools','measurement_mode','measurement_system','measurement_method','measurement_protocol',
                                                 'min_value', 'max_value', 'mean', 'stdev', 'median_value',
                                                 'sum_square', 'sum_square/frequency', 'percentile_25',
                                                 'percentile_50', 'percentile_75'])

        summary.to_csv('./synthese/{}_summary.csv'.format(self.data_sortie), index=False, sep=';')