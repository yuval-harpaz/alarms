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
if len(ihaa) > 0:
    idb = [x for x in range(len(db)) if db['pid'][x] not in haa['pid'].values]
    tosave = False
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
            tosave = True
    if len(np.unique(haa['pid'][~haa['pid'].isnull()])) < len(haa['pid'][~haa['pid'].isnull()]):
        raise Exception('not unique pid in haa')
    if tosave:
        haa.to_csv('data/deaths_haaretz+.csv', index=False)
        print('saved data/deaths_haaretz+.csv')
##
db = pd.read_csv('data/oct7database.csv')
haa = pd.read_csv('data/deaths_haaretz+.csv')
ihaa = np.where(haa['pid'].isnull())[0]
if len(ihaa) > 0:
    add = pd.read_csv('data/oct7database_additional.csv')
    # idb = [x for x in range(len(db)) if db['pid'][x] not in haa['pid'].values]
    # tosave = False
    for ii in ihaa:
        row = len(db)
        pid = int(np.max(list(db['pid']) + list(add['pid'])) + 1)
        db.at[row, 'pid'] = pid
        haa.at[ii, 'pid'] = pid
        name = haa['name'][ii].split(' ')
        db.at[row, 'שם פרטי'] = name[0]
        db.at[row, 'שם משפחה'] = name[-1]
        if len(name) < 2:
            db.at[row, 'שם נוסף'] = ' '.join(name[1:-1])
        db.at[row, 'Age'] = haa['age'][ii]
        db.at[row, 'Gender'] = haa['gender'][ii]
        db.at[row, 'Residence'] = haa['from'][ii]
        if haa['status'][ii] == 'אזרח':
            db.at[row, 'Role'] = 'אזרח'
        db.at[row, 'Status'] = 'killed'
        db.at[row, 'Event date'] = haa['death_date'][ii]
        db.at[row, 'first name'] = '??'
        db.at[row, 'last name'] = '??'
        print(haa['name'][ii] + ' ' + haa['story'][ii])
    haa.to_csv('data/deaths_haaretz+.csv', index=False)
    db.to_csv('data/oct7database.csv', index=False)
    print('saved haaretz+ data to data/oct7database.csv')


