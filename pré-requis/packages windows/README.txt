installez les drivers USB pour les telephones (ADB drivers)
installez les drivers USB pour les oscilloscopes (monsoon ou HS5)

pour le monsoon:
	- installer une des deux versions disponible.
	- une fois le pilote reconnue, utiliser libusb pour ecraser le pilote nouvellement installé

pour le HS5 :
	- installez la librairie pour les oscilloscopes (libtiepie 32x ou 64x)
	- 7.2.1 pour w7 et + avec mise a jours manquantes
	  8.1.4 pour w7 et + Mise a jour OK

placez la dll 32x ou 64x de libtiepie et Qt5 à la racine du dossier "Dobot Tester"
installer monsoon via le setup
installer via pip:
- pillow
- pyserial