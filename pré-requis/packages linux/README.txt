0/ retirer le "secured path" dans etc/sudoers, cela evitera d'avoir des problemes avec beaucoup de commandes.

1/ installez python 2.7 via Anaconda (beaucoup plus pratique pour l'intégralité des bibliothèques)

2/ executez le script shell 32 ou 64 pour installer toutes les bibliotheques necessaires (et les dlls)

s'il y a un bug, executer vous même ligne par ligne le code.

3/ vous n'avez plus qu'a lancer "sudo python main.py"

pour desactiver la charge USB: uiliser l'apk fourni dans apkusbdisabled

si nécessaire : pour monter un telephone correctement:

sudo wget -O /etc/udev/rules.d/51-android.rules https://raw.githubusercontent.com/NicolasBernaerts/ubuntu-scripts/master/android/51-android.rules
sudo chmod a+r /etc/udev/rules.d/51-android.rules
sudo service udev restart
sudo apt-get install android-tools-adb android-tools-fastboot

pour monter correctement un telephone:

	1. Enable Developer options and enable USB debugging.
	2. Install necessary modules to your computer:
	sudo apt-get install mtp-tools mtpfs
	3. Configure 51-android.rules:
	sudo gedit /etc/udev/rules.d/51-android.rules
	paste the following at the end of the file (if the file does not exist then just paste):
	#LG - Nexus 4
	SUBSYSTEM=="usb", ATTR{idVendor}=="1004", MODE="0666"
	#Samsung - Nexus 7 & 10
	SUBSYSTEM=="usb", SYSFS{idVendor}=="18d1", MODE="0666"

	Save and exit.
	4. Make the file executable:
	sudo chmod +x /etc/udev/rules.d/51-android.rules
	5. Restart udev
	sudo service udev restart
	6. Create mount point and permissions (will need to do this for other Nexus' if using for the 7 or 10)
	sudo mkdir /media/nexus4
	sudo chmod 755 /media/nexus4

	7. Plug in the Nexus 4 and make sure MTP is enabled.

	8. Mount with the following command:
	sudo mtpfs -o allow_other /media/nexus4

	9. When you have completed your work you must unmount:
	sudo umount /media/nexus4

	Now each time you need to copy from/to your Nexus 4 to your Linux computer you only need to plug in and run 8, then 9 when you have completed your work. 
