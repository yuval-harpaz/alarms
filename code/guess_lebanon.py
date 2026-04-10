import pandas as pd
import numpy as np
import os
import sys
sys.path.append('./code')
from alarms_origin import guess_lebanon26

local = '/home/yuval/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

coo = pd.read_csv('data/coord.csv')
alarms = pd.read_csv('data/alarms.csv')
already = np.where(~alarms['origin'].isnull())[0][-1]
if already < len(alarms) - 1:
    df_missing = alarms[already+1:]
    df_missing = guess_lebanon26(df_missing)
    filled = np.sum(~df_missing['origin'].isnull())
    if filled > 0:
        # df_missing.to_csv('~/Documents/missing.csv')
        alarms.to_csv('data/alarms.csv', index=False)
        os.system('git add data/alarms.csv')
        os.system(f'git commit -m "Guessed Lebanon origin"')
        os.system('git pull --rebase')
        os.system('git push')
        # print('debug')
    else:
        print('no new alarms from lebanon detected')
else:
    print('no new alarms detected')

