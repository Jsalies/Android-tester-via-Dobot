
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
sudo easy_install PyLibTiePie-0.6.1.egg
sudo tar -xvzf ply-3.10.tar.gz
cd ply-3.10
sudo python3.5 setup.py install
cd ..
sudo rm -rf ply-3.10
conda update libgcc
conda install pyserial
sudo apt-get install android-tools-adb android-tools-fastboot
sudo apt-get install android-tools-adb android-tools-fastboot
sudo wget -O /etc/udev/rules.d/51-android.rules https://raw.githubusercontent.com/NicolasBernaerts/ubuntu-scripts/master/android/51-android.rules
sudo chmod a+r /etc/udev/rules.d/51-android.rules
sudo service udev restart
sudo apt-get install mtp-tools mtpfs
