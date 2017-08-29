# -*- coding: utf-8 -*-
import platform
from multiprocessing import Process


class Enregistrement():
    def __init__(self, ouputEnergyFileName, dataRead, temp1, freq1, temp2, freq2, type, TIME_INIT=None, frequency=None,
                 RESISTOR=None, GAIN=None):
        self.ouputEnergyFileName = ouputEnergyFileName
        self.dataRead = dataRead
        self.TIME_INIT = TIME_INIT
        self.frequency = frequency
        self.RESISTOR = RESISTOR
        self.GAIN = GAIN
        self.temp1 = temp1
        self.freq1 = freq1
        self.temp2 = temp2
        self.freq2 = freq2
        self.type = type
        self.correction = 0.75
        # on crée un subprocess pour pouvoir continuer de travailler (accelère considerablement la vitesse de travail)
        p = Process(target=self.run, args=())
        p.start()

    # methode d'enregistrement pour l'oscilloscope HS5
    def run(self):
        csv_file = open(self.ouputEnergyFileName, 'w+')
        try:
            csv_file.write(
                "Beginning Temperature : " + str(self.temp1) + "C,Beginning Frequency : " + str(
                    self.freq1) + "Hz,Ending Temperature : " + str(self.temp2) + "C" + ",Ending Frequency : " + str(
                    self.freq2) + "Hz\n")
            csv_file.write("Time(usecs),Power" + "\n")
            # Write csv file
            period = (1.0 / self.frequency) * 1e6
            block = 0
            numberOfBlocks = int(len(self.dataRead) / 2)
            print("Ecriture dans le fichier")
            # Si nous calculons les valeurs via le courant
            if type == 1:
                for var in range(numberOfBlocks):
                    for element in range(len(self.dataRead[0])):
                        v1 = (self.dataRead)[block][element]
                        v2 = (self.dataRead)[block + 1][element]
                        power = v1 * v2
                        csv_file.write(str(self.TIME_INIT) + "," + str(
                            round(self.correction * v1 * v2, 4)) + "\n")  # power on phone
                        self.TIME_INIT = self.TIME_INIT + period
                        if platform.system() == "Windows":
                            csv_file.flush()
                    block = block + 2
                csv_file.close()
            # si nous calculons les valeurs via le gain/resistance
            else:
                for var in range(numberOfBlocks):
                    for element in range(len(self.dataRead[0])):
                        csv_file.write(str(self.TIME_INIT) + ',')
                        self.TIME_INIT = self.TIME_INIT + period
                        v1 = (self.dataRead)[block][element]
                        v2 = (self.dataRead)[block + 1][element]
                        voltageDifference = float(v2 / self.GAIN)
                        current = voltageDifference / self.RESISTOR
                        power = v1 * current
                        csv_file.write(str(round(self.correction * power, 4)) + "\n")  # power on phone
                        if platform.system() == "Windows":
                            csv_file.flush()
                    block = block + 2
                csv_file.close()

        except Exception as e:
            print('Exception: ' + e.message)
            return False
        finally:
            if csv_file is not None:
                csv_file.close()
        return True
