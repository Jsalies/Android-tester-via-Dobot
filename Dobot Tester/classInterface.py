# -*- coding: utf-8 -*-
import platform
import PIL.Image
import PIL.ImageTk
import os
import simulation
import shellcommands as adb
import sys

try:
    from tkinter import *
    from tkinter import messagebox as msgbox
except:
    from Tkinter import *
    from Tkinter import messagebox as msgbox

class Interface():
    def __init__(self):
        #definition des variables globals
        self.pourcent=0
        #definition de la fenetre principale
        self.fenetre = Tk(className="Energy consumption tester - Dobot Magician")
        self.fenetre.resizable(width=False, height=False)
        self.Htrigger=(self.fenetre.winfo_screenwidth()-815)/2
        self.Vtrigger=(self.fenetre.winfo_screenheight()-615)/2
        self.fenetre.geometry('800x600+{}+{}'.format(int(self.Htrigger),int(self.Vtrigger)))
        self.fenetre.attributes("-alpha", 0.9)
        #definition de l'arriere plan
        self.monfond = PIL.Image.open("./pictures/background.jpeg")
        self.background = PIL.ImageTk.PhotoImage(self.monfond) 
        self.Fond=Label(self.fenetre,image=self.background).place(x=-2,y=-2)
        #definition des titres
        self.txt1 = Label(self.fenetre, text ='caractéristiques de l\'écran du téléphone :',fg="white",font=("Helvetica", 10, "bold italic"),bg="black")
        self.txt2 = Label(self.fenetre, text ='instructions :',fg="white",font=("Helvetica", 10, "bold italic"),bg="black")
        self.txt3 = Label(self.fenetre, text ='Largueur (en Pixels) :',fg="white",anchor='e',font=("Helvetica", 10, "bold"),bg="black")
        self.txt4 = Label(self.fenetre, text ='Hauteur (en Pixels) :',fg="white",anchor='e',font=("Helvetica", 10, "bold"),bg="black")
        self.txt5 = Label(self.fenetre, text ='nombre de test :',fg="white",anchor='e',font=("Helvetica", 10, "bold"),bg="black")
        self.txt6 = Label(self.fenetre, text ='choix du scénario :',fg="white",font=("Helvetica", 10, "bold italic"),bg="black")
        self.txt7 = Label(self.fenetre, text ='mesure d\'energie :',fg="white",font=("Helvetica", 10, "bold italic"),bg="black")
        if sys.maxsize>2**32-1:
            version="x64"
        else:
            version="x86"
        self.txt8 = Label(self.fenetre, text = platform.system()+" Python v"+ str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])+" "+version,fg="white",font=("Helvetica", 7, "bold italic"),bg="black")
        #placement des titres
        self.txt1.place(height=20,width=400,x=0,y=10)
        self.txt2.place(height=20,width=400,x=400,y=10)
        self.txt3.place(height=20,width=150,x=20,y=50)
        self.txt4.place(height=20,width=150,x=20,y=100)
        self.txt5.place(height=20,width=150,x=20,y=150)
        self.txt6.place(height=20,width=124,x=138,y=190)
        self.txt7.place(height=20,width=120,x=540,y=190)
        self.txt8.place(height=20, width=250, x=610, y=582)
        #on récupere le systeme d'exploitation ainsi que la version de python
        #on definit une variable
        self.TexteInstructions = StringVar()
        self.TexteInstructions.set("Veuillez suivre les instructions apparaissantes ici.")
        #on defini notre zone de texte
        self.instruction=Label(self.fenetre,textvariable=self.TexteInstructions,bg='gray',justify="left",relief='sunken',anchor='nw')
        self.instruction.place(height=120,width=350,x=425,y=50)
        #definitions des entrées
        self.longvalue = IntVar()
        self.hautvalue = IntVar()
        self.longvalue.set(1000)
        self.hautvalue.set(1000)
        # notre fonction destiné à demander directement au telephone sa taille
        def autoAjust():
            # On demande directement au telephone sa taille
            try:
                size = adb.SizeScreen()
                self.longvalue.set(size[1])
                self.hautvalue.set(size[0])
            except:
                self.setInstruction("Veuillez renseigner la taille de l'écran du telephone")
        autoAjust()
        #definition du bouton AJUSTER
        self.ajust = Button(self.fenetre, text='L/H AUTO',bg='#797DF6',font=("ms serif", 10, "bold"), command=autoAjust)
        #placement du bouton LANCER
        self.ajust.place(height=20,width=100,x=270,y=50)
        #notre fonction qui affiche un pop-up d'aide.
        def helpMe():
            msgbox.showinfo(title="Manipulation à suivre",icon='question',default='ok',message="0/ Branchez le telephone, le Dobot et le(s) oscilloscope(s)\n1/ Indiquer la taille du telephone (Ou utilisez H/L AUTO).\n2/ Choisissez l'oscilloscope que vous souhaitez."
                                "\n3/ Choisissez la frequence d'echantillonage des mesures.\n4/ Choisissez un scénario à testé."
                                                    "\n5/ Lancez.\n6/ Suivez les instructions affichées dans le panneau haut droit.")
        #definition du bouton AIDE
        self.aide = Button(self.fenetre, text='AIDE',bg='#797DF6',font=("ms serif", 10, "bold"), command=helpMe)
        #placement du bouton AIDE
        self.aide.place(height=20,width=100,x=270,y=100)
        #Parametrage des entrées
        self.Longueur = Spinbox(self.fenetre,textvariable=self.longvalue, from_=1, to=10000,bg="gray")
        self.Hauteur = Spinbox(self.fenetre,textvariable=self.hautvalue, from_=1, to=10000,bg="gray")
        self.Nbscenar = Spinbox(self.fenetre, from_=1, to=500,bg="gray")
        self.Longueur.config()
        #placement des entrées
        self.Longueur.place(height=20,width=75,x=170,y=50)
        self.Hauteur.place(height=20,width=75,x=170,y=100)
        self.Nbscenar.place(height=20,width=75,x=170,y=150)
        #definition de la liste des scénarios
        self.liste = Listbox(self.fenetre,bg="gray")
        a=0
        for fichier in sorted(os.listdir('scenarios/')):
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
        #on defini une case à cocher
        self.tousScenarios= IntVar()
        self.toutfaire = Checkbutton(self.fenetre,variable=self.tousScenarios, text="Tout tester",bg="gray",activebackground="gray")        
        self.toutfaire.place(height=15,width=80,x=270,y=410)
        #on definit une variable
        self.TexteMesureEnergie = StringVar()
        self.TexteMesureEnergie.set("Ici apparaitrons les résultats du test")
        #on defini notre zone de texte
        self.MesureEnergie=Label(self.fenetre,textvariable=self.TexteMesureEnergie,justify="left",bg='gray',relief='sunken',anchor='nw')
        self.MesureEnergie.place(height=120,width=350,x=425,y=230)
        #on defini notre fond pour le choix de l'oscilloscope
        self.MesureEnergie=Label(self.fenetre,bg='gray',relief='sunken',anchor='nw')
        self.MesureEnergie.place(height=65,width=350,x=425,y=365)
        #○n defini les bouton pour régler la frequence de l'oscilloscope
        self.txt9 = Label(self.fenetre, text ='frequence :',fg="black",font=("Helvetica", 10, "bold italic"),bg="gray")
        self.txt9.place(height=20,width=100,x=665,y=370)    
        self.txt10 = Label(self.fenetre, text ='Hz',fg="black",font=("Helvetica", 10, "bold italic"),bg="gray")
        self.txt10.place(height=20,width=20,y=402,x=745)         
        self.frequence = IntVar()
        self.frequence.set(10000)
        self.valeurfrequence = Spinbox(self.fenetre,textvariable=self.frequence, from_=5000, to=200000,bg="gray")
        self.valeurfrequence.place(width=80,height=20,y=402,x=665)
        # on force la valeur de la frequence pour le monsoon
        self.tempo=10000
        def blocage():
            self.tempo=self.frequence.get()
            self.frequence.set(5000)
            self.valeurfrequence.configure(state=DISABLED)

        def deblocage():
            self.frequence.set(self.tempo)
            self.valeurfrequence.configure(state=NORMAL)
        # on defini les boutons pour choisir l'oscilloscope
        self.txt8 = Label(self.fenetre, text='choix de l\'oscilloscope :', fg="black",
                          font=("Helvetica", 10, "bold italic"), bg="gray")
        self.txt8.place(height=20, width=200, x=437, y=370)
        self.ChoixOscillo = StringVar()
        self.oscillo1 = Radiobutton(self.fenetre, text="HS5", variable=self.ChoixOscillo, value=1, bg="gray",
                                    activebackground="gray", command=deblocage)
        self.oscillo2 = Radiobutton(self.fenetre, text="Monsoon", variable=self.ChoixOscillo, value=2, bg="gray",
                                    activebackground="gray", command=blocage)
        self.oscillo1.select()
        # on place les boutons pour choisir l'oscilloscope
        self.oscillo1.place(y=400, x=580)
        self.oscillo2.place(y=400, x=440)
        #on definit une variable (% de la barre)
        self.pourcentafficher = StringVar()
        self.pourcentafficher.set("0%")
        self.pourcentaffichage=Label(self.fenetre,textvariable=self.pourcentafficher,bg='black',fg="white",font=("Helvetica", 14, "bold italic"),anchor='w')
        self.pourcentaffichage.place(height=30,width=70,x=710,y=528)
        #creation du de la barre de chargement
        self.Loading = Canvas(self.fenetre, width=200, height=100,bg='white',relief="ridge",borderwidth=5)
        self.Loading.place(height=50,width=600,x=100,y=520)
        self.monimage = PIL.Image.open("./pictures/progressbar.bmp")    ## Chargement d'une image à partir de PIL
        self.photo = PIL.ImageTk.PhotoImage(self.monimage)      
        def boost():
            value=float(self.pourcent)*5.88
            self.bar = Canvas(self.Loading, width=600,height=100,bg='white',borderwidth=0)
            self.bar.place(height=38,width=value,x=7,y=7)
            self.bar.create_image(300,0,image=self.photo)      
        boost()
        def Init():
            try:
                thread1=simulation.Simulation(self)
                thread1.start()
            except:
                self.TexteInstructions.set("Veuillez selectionner un scénario dans la liste\nOu cocher la case \"Tout tester\"")

        #definition du bouton LANCER
        self.bouton = Button(self.fenetre, text='LANCER',bg='#797DF6',font=("ms serif", 10, "bold"), command=Init)
        #placement du bouton LANCER
        self.bouton.place(height=30,width=100,x=350,y=460)
        #on crée une variable pour savoir quand on appuie sur entrer
        self.entrer=0
        #on incremente une variable si la touche entrer est appuyée
        def active(event):
            self.entrer=1
        #on génère l'evenement pour incrémenter notre variable
        self.fenetre.bind_all('<Return>',active)
     
    def desactive(self):
        self.entrer=0
        
    def setInstruction(self,texte):
        self.TexteInstructions.set(texte)
        
    def setMesureEnergie(self,texte):
        self.TexteMesureEnergie.set(texte)
        
    def boost(self):
            value=float(self.pourcent)*5.88
            self.bar = Canvas(self.Loading, width=600,height=100,bg='white',borderwidth=0)
            self.bar.place(height=38,width=value,x=7,y=7)
            self.bar.create_image(300,0,image=self.photo) 
            
    def setpourcent(self,value):
        if (value>=0 and value<=100):
            self.pourcent=value
            self.pourcentafficher.set(str(round(value,1))+"%")
            self.boost()
            return
        elif(value<0):
            self.pourcent=0
            self.pourcentafficher.set("0%")
            self.boost()
            return
        else:
            self.pourcent=100
            self.pourcentafficher.set("100%")
            self.boost()
            
    def start(self): 
        self.fenetre.mainloop()
