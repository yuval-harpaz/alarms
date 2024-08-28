import pandas as pd
import os
import Levenshtein
import numpy as np


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

db = pd.read_csv('data/oct7database.csv')

# ynet = pd.read_csv('data/ynetlist.csv')
# ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0',' ')
# idf = pd.read_csv('data/deaths_idf.csv')
##
haa = pd.read_csv('data/deaths_haaretz+.csv')
ihaa = np.where(haa['pid'].isnull())[0]
idb = [x for x in range(len(db)) if db['pid'][x] not in haa['pid'].values]
for ii in ihaa:
    name = haa['name'][ii]
    dist = np.ones(len(idb), int)*10
    for jj in range(len(idb)):
        val = [db['שם פרטי'][idb[jj]], db['שם משפחה'][idb[jj]]]
        fit = 0
        dist[jj] = max(Levenshtein.distance(db['שם פרטי'][idb[jj]], name.split(' ')[0]),
                   Levenshtein.distance(db['שם משפחה'][idb[jj]], name.split(' ')[-1]))
    cand = np.where(dist == min(dist))[0]
    if len(cand) == 1 and dist[cand[0]] < 3:
        print(name+' >>> '+db['שם פרטי'][idb[cand[0]]]+' '+db['שם משפחה'][idb[cand[0]]])
        haa.at[ii, 'pid'] = db['pid'][idb[cand[0]]]
if len(np.unique(haa['pid'][~haa['pid'].isnull()])) < len(haa['pid'][~haa['pid'].isnull()]):
    raise Exception('not unique pid in haa')
haa.to_csv('data/deaths_haaretz+.csv', index=False)
##
