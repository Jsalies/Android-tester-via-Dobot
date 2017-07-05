import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from os import listdir
from os.path import isfile, join
import sys

significae_value = 0.05

sys.stdout = open(sys.argv[1], 'w')

folder_path = sys.argv[2]

files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

cpt_echec = 0
echec_list = ""

data_list = []

for file in files:
    if file.endswith(".energy"):
        data_list.append(pd.read_csv(folder_path + file, skiprows=1, header=None)[1])
    else:
        data_list.append(None)

for i in range(len(files) - 1):
    for j in range(i + 1, len(files)):
        if files[i].endswith(".energy"):
            data_size = min(len(data_list[i]), len(data_list[j]))
            result = stats.wilcoxon(data_list[i][:data_size], data_list[j][:data_size])
            status = "same"
            if int(result.pvalue) > significae_value:
                status = "not same"
                cpt_echec += 1

            row = '| {}\t | {}\t | {}\t | {}\t | {}\t | {}\t\t | {}\t |' \
                .format(files[i], np.mean(data_list[i][:data_size]), files[j], np.mean(data_list[j][:data_size]),
                        result.statistic, result.pvalue, status)
            print("-" * len(row) + "\n" + row + "\n" + "-" * len(row) )



print("the non same dataset is {}".format(cpt_echec))
