import pandas as pd
import numpy as np
import os

areas = pd.read_csv('data/coord_area.csv')
areas_tab = pd.read_csv('data/polygons.tsv', sep='\t', header=None, index_col=None)
for ii in range(len(areas)):
    next_row = len(areas_tab)
    new = areas.loc[ii].values
    new = [new[0]] + [n.strip() for n in new[1].split(';')]
    until = len(new)
    for jj in range(until):
        areas_tab.at[next_row, jj] = new[jj]
areas_tab.to_csv('data/coord_area.tsv', sep='\t', header=None, index=None)