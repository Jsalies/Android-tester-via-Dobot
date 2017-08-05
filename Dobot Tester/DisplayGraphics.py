# -*- coding: utf-8 -*-
import os
from multiprocessing.pool import Pool
import matplotlib.pyplot as plt
import scipy.signal
import time
import pandas as pd


def graphicsCalculs(values):
    deb=time.time()
    data = pd.read_csv("./ressources/graph/"+values[0], skiprows=1)['Power']
    if os.stat("./ressources/graph/"+values[0])[6]/1000000.>20:
        pas=25
    else:
        pas=1
    """
    if values[2]==1:
        pas=25
    else:
        pas=1
    """
    data = scipy.signal.savgol_filter(data[0:len(data):pas], values[1], 3)
    print(values[0]+" : "+str(round(time.time()-deb,2))+"secs")
    return data

class graphics():

    def __init__(self,oscillotype,smoothingValues=5001):
        self.resultat=[]
        self.oscillotype=oscillotype
        self.smoothingValues=smoothingValues
        self.run()

    def run(self):
        deb = time.time()
        multiListe=[]
        for file in sorted(os.listdir("./ressources/graph/")):
            multiListe.append([file,self.smoothingValues,self.oscillotype])
        multiprocessing=Pool(4)
        self.resultat = multiprocessing.map(graphicsCalculs, multiListe)
        LenMin=len(self.resultat[0])
        for curve in self.resultat:
            if LenMin>len(curve):
                LenMin=len(curve)
            plt.plot(curve)
        Moyenne=LenMin*[0]
        for curve in self.resultat:
            Moyenne+=curve[0:LenMin]
        plt.plot(Moyenne/len(self.resultat),"b:",linewidth=3)
        print("durée total de la génération de graph : " + str(round(time.time() - deb, 2)) + "secs")
        plt.show()