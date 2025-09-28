import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
areas = pd.read_csv('data/coord_area.tsv', sep='\t', header=None)
# plot poligons with marker 1, 2, 3 for every point
colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']*50
plt.figure()
count = 0
for ii in range(len(areas)):
    coo = areas.iloc[ii, 1:].values
    lon = [float(c.split(', ')[1]) for c in [co for co in coo if type(co) == str]]
    lat = [float(c.split(', ')[0]) for c in [co for co in coo if type(co) == str]]

    plt.plot(lon + [lon[0]], lat + [lat[0]], color=colors[ii], linewidth=2)
    for jj in range(len(lon)):
        count += 1
        plt.text(lon[jj], lat[jj], str(count), color=colors[ii], fontsize=13)
    