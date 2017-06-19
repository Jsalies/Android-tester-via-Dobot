# -*- coding: utf-8 -*-
from Tkinter import *
from PIL import Image, ImageTk
import os
import test2

class Interface():
    
    def __init__(self):
        #definition des variables globals
        self.pourcent=0
        #definition de la fenetre principale
        self.fenetre = Tk(className="Energy consumption tester - Dobot Magician")
        self.Htrigger=(self.fenetre.winfo_screenwidth()-815)/2
        self.Vtrigger=(self.fenetre.winfo_screenheight()-615)/2
        self.fenetre.geometry('800x600+{}+{}'.format(self.Htrigger,self.Vtrigger))
        #definition des titres
        self.txt1 = Label(self.fenetre, text ='caractéristiques de l\'écran du téléphone :')
        self.txt2 = Label(self.fenetre, text ='instructions :')
        self.txt3 = Label(self.fenetre, text ='Largueur (en Pixels) :',anchor='e')
        self.txt4 = Label(self.fenetre, text ='Hauteur (en Pixels) :',anchor='e')
        self.txt5 = Label(self.fenetre, text ='nombre de test :',anchor='e')
        self.txt6 = Label(self.fenetre, text ='choix du scénario :')
        self.txt7 = Label(self.fenetre, text ='mesure d\'energie :')
        #placement des titres
        self.txt1.place(height=20,width=400,x=0,y=10)
        self.txt2.place(height=20,width=400,x=400,y=10)
        self.txt3.place(height=20,width=150,x=0,y=50)
        self.txt4.place(height=20,width=150,x=0,y=100)
        self.txt5.place(height=20,width=150,x=0,y=150)
        self.txt6.place(height=20,width=400,x=0,y=190)
        self.txt7.place(height=20,width=400,x=400,y=190)
        #definitions des entrées
        self.Longueur = Spinbox(self.fenetre, from_=0, to=10000)
        self.Hauteur = Spinbox(self.fenetre, from_=0, to=10000)
        self.Nbscenar = Spinbox(self.fenetre, from_=0, to=500)
        #placement des entrées
        self.Longueur.place(height=20,width=150,x=170,y=50)
        self.Hauteur.place(height=20,width=150,x=170,y=100)
        self.Nbscenar.place(height=20,width=150,x=170,y=150)
        #definition de la liste des scénarios
        self.liste = Listbox(self.fenetre)
        a=0
        for fichier in os.listdir('scenarios/'):
            a+=1
            self.liste.insert(a, fichier)
        #placement de la ligne des scénarios
        self.liste.place(height=200,width=329,x=25,y=230)
        #definition de la barre de scroll
        self.sc=Scrollbar(command=self.liste.yview)
        #postionnement de la barre de scroll
        self.sc.place(height=200,width=20,x=350,y=230)
        #configuration de la barre de scroll
        self.liste.configure(yscrollcommand=self.sc.set)
        #on definit une variable
        self.TexteInstructions = StringVar()
        self.TexteInstructions.set("Veuillez suivre les instructions apparaissantes ici.")
        #on defini notre zone de texte
        self.instruction=Label(self.fenetre,textvariable=self.TexteInstructions,bg='white',relief='sunken',anchor='nw')
        self.instruction.place(height=120,width=350,x=425,y=50)        
        #on definit une variable
        self.TexteMesureEnergie = StringVar()
        self.TexteMesureEnergie.set("Ici apparaitrons les résultats du test")
        #on defini notre zone de texte
        self.MesureEnergie=Label(self.fenetre,textvariable=self.TexteMesureEnergie,bg='white',relief='sunken',anchor='nw')
        self.MesureEnergie.place(height=200,width=350,x=425,y=230)
        #creation du de la barre de chargement
        self.Loading = Canvas(self.fenetre, width=200, height=100,bg='white',relief="ridge",borderwidth=5)
        self.Loading.place(height=50,width=600,x=100,y=520)
        self.monimage = Image.open("progressbar.bmp")    ## Chargement d'une image à partir de PIL
        self.photo = ImageTk.PhotoImage(self.monimage)      
        def boost():
            value=float(self.pourcent)*5.88
            self.bar = Canvas(self.Loading, width=600,height=100,bg='white',borderwidth=0)
            self.bar.place(height=38,width=value,x=7,y=7)
            self.bar.create_image(300,0,image=self.photo)       
        boost()
        def Init():
            L=self.Longueur.get()
            H=self.Hauteur.get()
            Nb=self.Nbscenar.get()
            Scenar=self.liste.get(self.liste.curselection())
            thread1=test2.Afficheur(self)
            thread1.start()
        #definition du bouton LANCER
        self.bouton = Button(self.fenetre, text='LANCER', command=Init)
        #placement du bouton LANCER
        self.bouton.place(height=30,width=100,x=350,y=460)

    def setInstruction(self,texte):
        self.TexteInstructions.set(texte)
        
    def setMesureEnergie(self,texte):
        self.TexteMesureEnergie.set(texte)
    
    def setpourcent(self,value):
        if (value>=0 and value<=100):
            self.pourcent=value
            return
        elif(value<0):
            self.pourcent=0
            return
        else:
            self.pourcent=100 
    def start(self): 
        self.fenetre.mainloop()