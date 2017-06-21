#!/usr/bin/python
import sys, getopt

def process(line):
    output = line.replace('solo.clickOnScreen','mov')
    output = output.replace('solo.sleep','wait')
    output = output.replace('solo.goBack()','return')
    output = output.replace(';',' ').replace('F','')
    output = output.replace('solo.Dragfrom','scroll')
    return output


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
    outputFile.write(inputFilePath +'\n)
    for line in open(inputfilePath,'r'):
        if line.find("//") < 0 and len(line.strip()) >0:
            processedLine = process(line.strip()).strip('')
            if processedLine.find("mov") >= 0 :
                processedLine += "touch()"
            outputFile.write(processedLine +'\n')
    outputFile.close()


if __name__ == "__main__":
   main(sys.argv[1:])
