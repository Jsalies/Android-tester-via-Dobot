echo "Is Anaconda for python 2.7 installed??? (yes/no)"
read answer

while [ $answer != 'yes' ] && [ $answer != 'no' ]
do
	echo "yes or no : "
	read answer
done

if [ $answer = 'no' ]
then
	echo "ok... install it and come back later"
	exit
fi

echo "Which kind of architecture do you use??? (64/32)"
read answer

while [ $answer != '64' ] && [ $answer != '32' ]
do
	echo "64 or 32 : "
	read answer
done

if [ $answer = '64' ]
then
	echo "libtiepie installation for os 64 bits : "
	sudo mkdir tempo
	sudo tar -xvzf libtiepie-0.6.7.GNULinux-x86-64.tar.gz -C tempo
	cd tempo/
	sudo ./install.sh
	cd ..
	sudo rm -rf tempo/
	sudo cp "Qt5dlls 64x/libQt5Core.so.5" "/usr/lib/libQt5Core.so.5"
	sudo cp "Qt5dlls 64x/libQt5Network.so.5" "/usr/lib/libQt5Network.so.5"
	sudo cp "Qt5dlls 64x/libQt5SerialPort.so.5" "/usr/lib/libQt5SerialPort.so.5"
else
	echo "libtiepie installation for os 32 bits : "
	sudo mkdir tempo
	sudo tar -xvzf libtiepie-0.6.7.GNULinux-x86.tar.gz -C tempo
	cd tempo/
	sudo ./install.sh
	cd ..
	sudo rm -rf tempo/
	sudo cp "Qt5dlls 32x/libQt5Core.so.5" "/usr/lib/libQt5Core.so.5"
	sudo cp "Qt5dlls 32x/libQt5Network.so.5" "/usr/lib/libQt5Network.so.5"
	sudo cp "Qt5dlls 32x/libQt5SerialPort.so.5" "/usr/lib/libQt5SerialPort.so.5"
fi

sudo easy_install PyLibTiePie-0.6.1.egg
sudo tar -xvzf ply-3.10.tar.gz
cd ply-3.10
sudo python3.5 setup.py install
cd ..
sudo rm -rf ply-3.10
conda update libgcc
conda install pyserial
sudo apt-get install adb
echo "Take a look, perhaps an error occurred??.... (then press ENTER)
read answer

