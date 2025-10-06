import pandas as pd
import numpy as np   
import os

miss = pd.read_csv('~/Documents/oct7database - no coord.csv')
miss.sort_values('שם משפחה', inplace=True)
txt = ''
for ii in range(len(miss)):
    txt += f"{miss.iloc[ii]['שם משפחה']} {miss.iloc[ii]['שם פרטי']} {miss.iloc[ii]['שם נוסף']}, "
print(txt)
txt = txt.replace(' nan,', ',')
with open('/home/innereye/Documents/missing.txt', 'w') as f:
    f.write(txt)
