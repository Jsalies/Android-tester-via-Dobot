# -*- coding: utf-8 -*-

from Tkinter import *
from PIL import Image, ImageTk
import os
            
#-----------------------------DEFINITION DE L'INTERFACE GRAPHIQUE-----------------------------------    
      
#definition des variables globals
pourcent=0

#definition de la fenetre principale
fenetre = Tk(className="Energy consumption tester - Dobot Magician")
Htrigger=(fenetre.winfo_screenwidth()-815)/2
Vtrigger=(fenetre.winfo_screenheight()-615)/2
fenetre.geometry('800x600+{}+{}'.format(0,0))

#definition des titres
txt1 = Label(fenetre, text ='caractéristiques de l\'écran du téléphone :')
txt2 = Label(fenetre, text ='instructions :')
txt3 = Label(fenetre, text ='Largueur (en Pixels) :',anchor='e')
txt4 = Label(fenetre, text ='Hauteur (en Pixels) :',anchor='e')
txt5 = Label(fenetre, text ='nombre de test :',anchor='e')
txt6 = Label(fenetre, text ='choix du scénario :')
txt7 = Label(fenetre, text ='mesure d\'energie :')

#placement des titres
txt1.place(height=20,width=400,x=0,y=10)
txt2.place(height=20,width=400,x=400,y=10)
txt3.place(height=20,width=150,x=0,y=50)
txt4.place(height=20,width=150,x=0,y=100)
txt5.place(height=20,width=150,x=0,y=150)
txt6.place(height=20,width=400,x=0,y=190)
txt7.place(height=20,width=400,x=400,y=190)

#definitions des entrées
Longueur = Spinbox(fenetre, from_=0, to=10000)
Hauteur = Spinbox(fenetre, from_=0, to=10000)
Nbscenar = Spinbox(fenetre, from_=0, to=500)

#placement des entrées
Longueur.place(height=20,width=150,x=170,y=50)
Hauteur.place(height=20,width=150,x=170,y=100)
Nbscenar.place(height=20,width=150,x=170,y=150)

#definition de la liste des scénarios
liste = Listbox(fenetre)
a=0
for fichier in os.listdir('scenarios/'):
    a+=1
    liste.insert(a, fichier)

#placement de la ligne des scénarios
liste.place(height=200,width=329,x=25,y=230)

#definition de la barre de scroll
sc=Scrollbar(command=liste.yview)

#postionnement de la barre de scroll
sc.place(height=200,width=20,x=350,y=230)

#configuration de la barre de scroll
liste.configure(yscrollcommand=sc.set)

#on definit une variable
TexteInstructions = StringVar()
TexteInstructions.set("bonjour")

def setInstruction(texte):
    global TexteInstructions
    TexteInstructions.set(texte)
    
#on defini notre zone de texte
instruction=Label(fenetre,textvariable=TexteInstructions,bg='white',relief='sunken',anchor='nw')
instruction.place(height=120,width=350,x=425,y=50)

#on definit une variable
TexteMesureEnergie = StringVar()
TexteMesureEnergie.set("bonjour")

def setMesureEnergie(texte):
    global TexteMesureEnergie
    TexteMesureEnergie.set(texte)
    
#on defini notre zone de texte
MesureEnergie=Label(fenetre,textvariable=TexteMesureEnergie,bg='white',relief='sunken',anchor='nw')
MesureEnergie.place(height=200,width=350,x=425,y=230)

#creation du de la barre de chargement
Loading = Canvas(fenetre, width=200, height=100,bg='white',relief="ridge",borderwidth=5)
Loading.place(height=50,width=600,x=100,y=520)
monimage = Image.open("progressbar.bmp")    ## Chargement d'une image à partir de PIL
photo = ImageTk.PhotoImage(monimage) 

def setpourcent(value):
    global pourcent
    if (value>=0 and value<=100):
        pourcent=value
        return
    elif(value<0):
        pourcent=0
        return
    else:
        value=100 
        
def boost():
    global pourcent
    value=float(pourcent)*5.88
    bar = Canvas(Loading, width=600,height=100,bg='white',borderwidth=0)
    bar.place(height=38,width=value,x=7,y=7)
    bar.create_image(300,0,image=photo)

def Init():
    L=Longueur.get()
    H=Hauteur.get()
    Nb=Nbscenar.get()
    Scenar=liste.get(liste.curselection())
    print "bob"
    
    
#definition du bouton LANCER
bouton = Button(fenetre, text='LANCER', command=Init)
#placement du bouton LANCER
bouton.place(height=30,width=100,x=350,y=460)

fenetre.mainloop()