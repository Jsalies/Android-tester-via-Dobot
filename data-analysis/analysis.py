import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from os import listdir
from os.path import isfile, join
import sys

significae_value = 0.05

sys.stdout = open(sys.argv[1], 'w')

folder_path1 = sys.argv[2]
folder_path2 = sys.argv[3]

files1 = [f for f in listdir(folder_path1) if isfile(join(folder_path1, f))]
files2 = [f for f in listdir(folder_path1) if isfile(join(folder_path1, f))]

cpt_echec = 0
echec_list = ""

data_list1 = []
data_list2 = []

for file in files1:
    if file.endswith(".energy"):
        data_list1.append(pd.read_csv(folder_path1 + file, skiprows=1, header=None)[1])
    else:
        data_list1.append(None)

for file in files2:
    if file.endswith(".energy"):
        data_list2.append(pd.read_csv(folder_path2 + file, skiprows=1, header=None)[1])
    else:
        data_list2.append(None)

for i in range(len(files1)):
    if files1[i].endswith(".energy"):
        for j in range(len(files2)):
            if files2[i].endswith(".energy"):
                data_size = min(len(data_list1[i]), len(data_list2[j]))
                result = stats.wilcoxon(data_list1[i][:data_size], data_list2[j][:data_size])
                status = "same"
                if int(result.pvalue) > significae_value:
                    status = "not same"
                    cpt_echec += 1

                row = '| {}\t | {}\t | {}\t | {}\t | {}\t | {}\t\t | {}\t |' \
                    .format(files1[i], np.mean(data_list1[i][:data_size]), files2[j], np.mean(data_list2[j][:data_size]),
                            result.statistic, result.pvalue, status)
                print("-" * len(row) + "\n" + row + "\n" + "-" * len(row) )



print("the non same dataset is {}".format(cpt_echec))
