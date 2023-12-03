import pandas as pd
import os
import Levenshtein
import numpy as np


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True


haa = pd.read_csv('data/deaths_haaretz.csv')
ynet = pd.read_csv('data/ynetlist.csv')
idf = pd.read_csv('data/war23_idf_deaths.csv')
##
found_idf = np.zeros((len(idf), 3), int)
found_idf[:, 1:] = -1
found_idf[:, 0] = np.arange(len(idf))
tbl = 0
for table in [ynet, haa]:
    tbl += 1
    if tbl == 1:
        age = table['גיל'].values
        val = []
        for jj in range(len(table)):
            val.append(table['שם פרטי'][jj]+' '+table['שם משפחה'][jj])
    else:
        val = table['name'].str.replace('׳', "'").values
        age = table['age'].values
    for ii in range(len(idf)):
        name = idf['name'][ii]
        for jj in range(len(val)):
            agefit = age[jj] == str(idf['age'][ii])
            if name in val[jj]:
                found_idf[ii, tbl] = jj
            else:
                fit = 0
                for part in name.split(' '):
                    if part in val[jj]:
                        fit += 1
                if fit > 1 and agefit:
                    found_idf[ii, tbl] = jj
                elif name.split(' ')[0] in val[jj] and agefit:
                    dist = []
                    for nm in name.split(' ')[1:]:
                        for vl in val[jj].split(' '):
                            dist.append(Levenshtein.distance(nm,vl))
                    if min(dist) < 2:
                        found_idf[ii, tbl] = jj
print(np.sum(found_idf == -1, 0))



##
# except Exception as e:
# print('war23_haaretz_kidnapped.py failed')
# a = os.system('echo "war23_haaretz_kidnapped.py failed" >> code/errors.log')
# b = os.system(f'echo "{e}" >> code/errors.log')
