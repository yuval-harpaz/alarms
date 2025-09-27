import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
areas = pd.read_csv('data/coord_area.csv')
# plot poligons with marker 1, 2, 3 for every point
plt.figure()
colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
count = 0
for ii in range(len(areas)):
    coo = areas['points'][ii]
    lon = [float(c.split(', ')[1]) for c in coo.split(';')]
    lat = [float(c.split(', ')[0]) for c in coo.split(';')]
    plt.plot(lon + [lon[0]], lat + [lat[0]], color=colors[ii], linewidth=2)
    for jj in range(len(lon)):
        count += 1
        plt.text(lon[jj], lat[jj], str(count), color=colors[ii], fontsize=13)
    