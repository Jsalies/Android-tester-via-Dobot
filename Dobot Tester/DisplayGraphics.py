# -*- coding: utf-8 -*-
import os,os.path
from multiprocessing.pool import Pool
import multiprocessing
import matplotlib.pyplot as plt
import scipy.signal
import time
import pandas as pd

class graphics():

    def __init__(self,oscillotype,smoothingValues=5001):
        self.smoothingValues=smoothingValues
        self.nbpross=int(multiprocessing.cpu_count()/2)
        self.run()

    def run(self):
        print("Génération des courbes :")
        # on génere nos variables
        deb = time.time()
        multifile=[]
        multidir=[]
        multiprocessing = Pool(self.nbpross)
        # on génere la liste des fichiers dossiers à parcourir
        FileAndDirectories("./ressources/graph/", multifile, multidir, self.smoothingValues)

        #on génere les courbes pour les fichiers directement dans ./ressources/graph/
        if len(multifile)!=0:
            print("calculs pour les fichiers dans : ./ressources/graph/ ...")
            debfile=time.time()
            resultat = multiprocessing.map(graphicsCalculs, multifile)
            pas=100./len(multifile)
            nbfile=len(multifile)
            LenMin = len(resultat[0])
            for curve in resultat:
                if LenMin>len(curve):
                    LenMin=len(curve)
                nbfile -= 1
                r,v,b=Get_RGB_Color(nbfile*pas)
                plt.plot(curve,color=(r,v,b))
            Moyenne = LenMin * [0]
            for curve in resultat:
                Moyenne += curve[0:LenMin]
            plt.plot(Moyenne / len(resultat), "b:", linewidth=3,label="Average")
            print("DONE!! (durée total : "+str(round(time.time()-debfile,1))+" secs)")

        #on génere les moyennes des courbes situées dans les dossiers de ./ressources/graph/
        for file in multidir:
            multifile = []
            mutltidir2 = []
            print("calculs pour les fichiers dans : ./ressources/graph/"+file+" ...")
            debdir = time.time()
            FileAndDirectories("./ressources/graph/"+file+"/", multifile, mutltidir2, self.smoothingValues)
            resultat = multiprocessing.map(graphicsCalculs, multifile)
            LenMin=len(resultat[0])
            for curve in resultat:
                if LenMin>len(curve):
                    LenMin=len(curve)
            Moyenne=LenMin*[0]
            for curve in resultat:
                Moyenne+=curve[0:LenMin]
            plt.plot(Moyenne/len(resultat),":",linewidth=3, label=file)
            print("DONE!! (durée total : " + str(round(time.time() - debdir,1)) + " secs)")

        #on affiche tout
        print("durée total de la génération des graphs : " + str(round(time.time() - deb, 2)) + "secs")
        plt.legend()
        plt.show()

def FileAndDirectories(path,filelist,dirlist, smoothingValues):
    """ permet de remplir deux listes contenant l'ensemble des fichier / dossiers de path"""
    for file in sorted(os.listdir(path)):
        if os.path.isfile(path + file):
            filelist.append([path+file, smoothingValues])
        else:
            dirlist.append(file)

def Get_RGB_Color(pourcent):
    """ prend une valeur entre 0 et 100 puis renvoie renvoie un code rvb équivalent au format (0-1, 0-1, 0-1)"""
    valeur=pourcent*15.3
    if(valeur>=0 and valeur<255):
        r=255
        v=valeur
        b=0
    elif (valeur >= 255 and valeur < 510):
        r=510-valeur
        v=255
        b=0
    elif (valeur >= 510 and valeur < 765):
        r=0
        v=255
        b=valeur-510
    elif (valeur >= 765 and valeur < 1020):
        r = 0
        v = 1020-valeur
        b = 255
    elif (valeur >= 1020 and valeur < 1275):
        r=valeur-1020
        v=0
        b=255
    else:
        r=255
        v=0
        b=1530-valeur

    #on renvoie la couleur au format rvb (0-1,0-1,0-1)
    return [r/255,v/255,b/255]

def graphicsCalculs(values):
    deb=time.time()
    #on ouvre le fichier csv representant notre courbe
    data = pd.read_csv(values[0], skiprows=1)['Power']
    #on regarde si c'est un fichier de plus de 20Mos (monsoon ou homesystem??)
    if os.stat(values[0])[6]/1000000.>20:
        pas=25
    else:
        pas=1
    #on lisse notre courbe
    data = scipy.signal.savgol_filter(data[0:len(data):pas], values[1], 3)
    print(values[0].split("/")[-1]+" : "+str(round(time.time()-deb,2))+"secs")
    #on retourne la courbe lissée
    return data