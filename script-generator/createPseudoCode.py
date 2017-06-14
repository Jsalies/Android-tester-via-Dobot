#!/usr/bin/python
import sys, getopt

def process(line):
    return line.replace('solo.clickOnScreen','mov').replace('solo.sleep','wait').replace('solo.goBack()','return')


def main(argv):
    inputfilePath=''
    outputfilePath=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print("test.py -i <inputfilePaht> -o <outputfilePath>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("test.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfilePath = arg
        elif opt in ("-o", "--ofile"):
            outputfilePath = arg
    outputFile = open(outputfilePath, 'w')

    for line in open(inputfilePath,'r'):
        if line.find("//") < 0 and len(line.strip()) >0:
            #print(process(line.strip()).rstrip('\n').strip(''))
            outputFile.write(process(line.strip()).strip('')+'\n')
    outputFile.close()


if __name__ == "__main__":
   main(sys.argv[1:])
