# -*- coding: utf-8 -*-
import os
from multiprocessing.pool import Pool
from threading import Thread
import pandas as pd
import numpy as np
import time

def description(Values):
    deb = time.time()
    # on ouvre notre csv
    data = pd.read_csv("./results/"+Values[0],skiprows=1)['Power']
    # on calculs toutes les valeurs pertinentes
    dmin = np.amin(data)
    dmax = np.amax(data)
    mean = np.mean(data)
    stdev = np.std(data)
    median = np.median(data)
    sum_square = np.sum(data ** 2)
    sum_square_divided_by_frequency = sum_square / float(Values[1])
    percentile_25 = np.percentile(data, 25)
    percentile_50 = np.percentile(data, 50)
    percentile_75 = np.percentile(data, 75)
    number_of_samples = len(data)
    print(Values[0] + " : " + str(time.time() - deb))
    return [Values[0],dmin,dmax,mean,stdev,median,sum_square,sum_square_divided_by_frequency,percentile_25,percentile_50,percentile_75,number_of_samples]

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

    def run(self):
        # On compte le nombre de fichiers à traiter
        deb=time.time()
        self.fenetre.setpourcent(0)
        if len(os.listdir(self.data_entree))==0:
            self.fenetre.setInstruction("le dossier \"./results\" est vide.")
            return
        pas=100./len(os.listdir(self.data_entree))
        self.fenetre.setInstruction("Debut de la syntheses des fichiers.")
        #pour chaque fichier dans./results/
        MultiListe=[]
        for file in sorted(os.listdir(self.data_entree)):
            if file.endswith('.csv'):
                MultiListe.append([file,self.frequency])
        multiprocessing=Pool(4)
        Values=multiprocessing.map(description,MultiListe)

        for resultat in Values:
            self.summary.append({
                'name': (resultat[0])[:(resultat[0]).rfind('-')],
                'id': (resultat[0])[(resultat[0]).rfind('-')+1:(resultat[0]).rfind('.')],
                'category': "\(O_O)/",
                'measurement_tools': self.measurement_tools,
                'measurement_mode': self.measurement_mode,
                'measurement_system': self.measurement_system,
                'measurement_method': self.measurement_method,
                'measurement_protocol': self.measurement_protocol,
                'min_value': resultat[1], 'number_of_samples': resultat[11],
                'max_value': resultat[2], 'mean': resultat[3], 'stdev': resultat[4],
                'median_value': resultat[5], 'sum_square': resultat[6],
                'sum_square/frequency': resultat[7],
                'percentile_25': resultat[8],
                'percentile_50': resultat[9],
                'percentile_75': resultat[10]})

            self.fenetre.setpourcent(self.fenetre.getpourcent()+pas)

        sorted(self.summary, key=lambda k: (k['name'], k['id']))
        summary = pd.DataFrame(self.summary, columns=['name', 'id', 'number_of_samples','category',
                    'measurement_tools','measurement_mode','measurement_system','measurement_method','measurement_protocol',
                                                 'min_value', 'max_value', 'mean', 'stdev', 'median_value',
                                                 'sum_square', 'sum_square/frequency', 'percentile_25',
                                                 'percentile_50', 'percentile_75'])

        summary.to_csv('./synthese/{}_summary.csv'.format(self.data_sortie), index=False, sep=';')
        self.fenetre.setInstruction("Travail terminé.\nTemps total pris pour la synthèse: " + str(round(time.time() - deb),2)+"secs")