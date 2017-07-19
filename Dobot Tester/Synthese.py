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
                    'number': file[file.rfind('-')+1:file.rfind('.')],
                    'min_value': dmin, 'number_of_samples': number_of_samples,
                    'max_value': dmax, 'mean': mean, 'stdev': stdev,
                    'median_value': median, 'sum_square': sum_square,
                    'sum_square/frequency': sum_square_divided_by_frequency,
                    'percentile_25': percentile_25,
                    'percentile_50': percentile_50,
                    'percentile_75': percentile_75})

                self.fenetre.setpourcent(self.fenetre.getpourcent()+pas)

        os.remove("tempo.csv")
        summary = pd.DataFrame(self.summary, columns=['name', 'number', 'number_of_samples',
                                                 'min_value', 'max_value', 'mean', 'stdev', 'median_value',
                                                 'sum_square', 'sum_square/frequency', 'percentile_25',
                                                 'percentile_50', 'percentile_75'])

        summary.to_csv('./synthese/{}_summary.csv'.format("test_complet"), index=False, sep=',')
