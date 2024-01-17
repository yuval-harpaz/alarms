import pandas as pd
import os
import numpy as np
import Levenshtein


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    # sys.path.append(local + 'code')

haa = pd.read_csv('data/deaths_haaretz+.csv')
names = pd.read_csv('data/oct_7_9.csv')
idf = pd.read_csv('data/deaths_idf.csv')
# names_row = np.array(names.index)+2
missing = []
for ii in range(2, len(names)+2):
    if ii not in haa['map_row'].values:
      missing.append(ii)

row = np.array([x for x in haa['map_row'] if not np.isnan(x)])
dup = []
for x in np.unique(row):
    if np.sum(row == x) > 1:
        dup.append(x)

maprow = 75
haarow = np.where(haa['map_row'] == maprow)[0][0]
print(haa['name'][haarow]+' '+names['fullName'][maprow-2])
missmatch = []
for ii in range(2, len(names)+2):
    haarow = np.where(haa['map_row'] == ii)[0][0]
    namem = names['fullName'][ii-2]
    rankm = str(names['rank'][ii-2]).replace("(מיל')",'').replace("(מיל׳)",'').replace('"', '״').strip()
    rankh = str(haa['rank'][haarow]).replace("(מיל')",'').replace("(מיל׳)",'').replace('"', '״').strip()
    jdf = haa['idf_row'][haarow]
    if ~np.isnan(jdf):  # type(jdf) == np.float64:
        ranki = idf['rank'][jdf-2].replace('במי','מי').replace("(מיל')",'').replace("(מיל׳)",'').replace('"', '״').strip()
        if ranki != rankm:
            missmatch.append(f'{namem} map: {rankm} idf: {ranki}')
#             names.at[ii-2, 'rank'] = idf['rank'][jdf-2]
# names.to_csv('data/oct_7_9.csv', index=False)
for ii in range(len(names)):
    rnk = names['rank'][ii]
    if type(rnk) == str:
        names.at[ii, 'rank'] = rnk.strip()

missmatch = []
for ii in range(2, len(names) + 2):
    haarow = np.where(haa['map_row'] == ii)[0][0]
    namem = names['fullName'][ii - 2]
    agem = str(names['age'][ii - 2])
    ageh = str(haa['rank'][haarow])
    jdf = haa['idf_row'][haarow]
    if ~np.isnan(jdf):  # type(jdf) == np.float64:
        agei = idf['age'][jdf - 2]
        if agei != int(float(agem)):
            missmatch.append(f'{namem} map: {agem} idf: {agei}')
            names.at[ii-2, 'age'] = float(idf['age'][jdf-2])

missmatch = []
for ii in range(2, len(names) + 2):
    haarow = np.where(haa['map_row'] == ii)[0][0]
    namem = names['fullName'][ii - 2]
    agem = names['age'][ii - 2]
    ageh = haa['age'][haarow]
    # jdf = haa['idf_row'][haarow]
    if ~np.isnan(ageh):  # type(jdf) == np.float64:
        # agei = idf['age'][jdf - 2]
        if np.abs(ageh - agem) > 1:
            missmatch.append([namem,agem,ageh])

missmatch = []
for ii in range(2, len(names) + 2):
    haarow = np.where(haa['map_row'] == ii)[0][0]
    namem = names['fullName'][ii - 2]
    agem = names['age'][ii - 2]
    ageh = haa['age'][haarow]
    # jdf = haa['idf_row'][haarow]
    # if ~np.isnan(jdf):  # type(jdf) == np.float64:
    #     agei = idf['age'][jdf - 2]
    if np.abs(agem - ageh) > 1:
        missmatch.append(f'{namem} map: {agem} haa: {ageh}')
        haa.at[haarow, 'age'] = agem
haa.to_csv('data/deaths_haaretz+.csv', index=False)