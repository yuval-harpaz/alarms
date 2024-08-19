import pandas as pd
import os
import numpy as np
import sys
sys.path.append('code')

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
file = open('/home/innereye/Documents/kfar_aza.txt')
txt = file.read().split('\n')
file.close()
txt = [x for x in txt if len(x) > 0]

df = pd.DataFrame(columns=['name', 'coo'])
for ii in range(0, len(txt), 3):
    df.loc[int(ii/3)] = [txt[ii+2], txt[ii+1].replace('(','').replace(')','')]

df.to_csv('~/Documents/kacoo.csv', index=False)