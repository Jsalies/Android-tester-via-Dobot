#!/usr/bin/python
import sys, getopt

def process(line):
    return line.replace('solo.clickOnScreen','mov').replace('solo.sleep','wait').replace('solo.goBack()','return').replace(';',' ').replace('F','')


def main(argv):
    inputfilePath=''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print("test.py -i <inputfilePaht>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("test.py -i <inputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfilePath = arg
    outputFile = open(inputfilePath+".out", 'w')

    for line in open(inputfilePath,'r'):
        if line.find("//") < 0 and len(line.strip()) >0:
            #print(process(line.strip()).rstrip('\n').strip(''))
            processedLine = process(line.strip()).strip('')
            if processedLine.find("mov") >= 0 :
                processedLine += "touch()"
            outputFile.write(processedLine +'\n')
    outputFile.close()


if __name__ == "__main__":
   main(sys.argv[1:])
