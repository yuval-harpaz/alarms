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
idf = pd.read_csv('data/deaths_idf.csv')
##
found_idf = np.zeros((len(idf), 3), int)
found_idf[:, 1:] = -1
found_idf[:, 0] = np.arange(len(idf))
tbl = 0
for table in [ynet, haa]:
    tbl += 1
    if tbl == 1:
        age = table['גיל'].values
        fro = table['מקום מגורים'].values
        val = []
        for jj in range(len(table)):
            val.append(table['שם פרטי'][jj]+' '+table['שם משפחה'][jj])
    else:
        val = table['name'].str.replace('׳', "'").values
        age = table['age'].values
        fro = table['from'].values
    for ii in range(len(idf)):
        name = idf['name'][ii]
        for jj in range(len(val)):
            agefit = age[jj] == str(idf['age'][ii])
            if name in val[jj]:
                if agefit:
                    found_idf[ii, tbl] = jj
                else:
                    print(f'{name} ages: {age[jj]} {idf["age"][ii]}')
                    if type(fro[jj]) == str and Levenshtein.distance(fro[jj], idf['from'][ii]) < 2:
                        found_idf[ii, tbl] = jj
                    else:
                        print(f'{name} locs: {fro[jj]} {idf["from"][ii]}')
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
found_idf[np.where(idf['name'].str.contains('עלים'))[0], 2] = np.where(haa['name'].str.contains('עלים'))[0][0]
found_idf[np.where(idf['name'].str.contains('יהונתן אהרן שטיינברג'))[0], 2] = np.where(haa['name'].str.contains('יהונתן אהרן שטיינברג'))[0][0]
ormizrahi = np.where(idf['name'].str.contains('אור מזרחי'))
print(np.sum(found_idf == -1, 0))

##
log = 'idf not in haaretz: '+', '.join(idf['name'][found_idf[:,2] == -1].values)+'\n'
log = log + 'idf not in ynet: '+', '.join(idf['name'][found_idf[:,1] == -1].values)+'\n'
err = [x for x in range(len(haa)) if x not in found_idf[:,2]]
err = np.array(err)[haa['status'].values[err] == 'חייל']
log = log + 'haaretz not in idf:' + ', '.join(haa['name'][err]) + '\n'
print(log)

##
df = idf.copy()
for ii in range(len(idf)):
    if found_idf[ii, 2] > -1:
        df.at[ii, 'haaretz'] = haa['story'][found_idf[ii, 2]]
    else:
        df.at[ii, 'haaretz'] = ''
    if found_idf[ii, 1] > -1:
        df.at[ii, 'ynet'] = ynet['מידע על המוות'][found_idf[ii, 1]]
        df.at[ii, 'first'] = ynet['שם פרטי'][found_idf[ii, 1]]
        df.at[ii, 'last'] = ynet['שם משפחה'][found_idf[ii, 1]]
    else:
        df.at[ii, 'ynet'] = ''
        df.at[ii, 'first'] = idf['name'][ii].split(' ')[0]
        df.at[ii, 'last'] = ' '.join(idf['name'][ii].split(' ')[1:])
df['status'] = 'חייל'
##
ihaa = [x for x in range(len(haa)) if x not in found_idf[:,2]]
ihaa = np.sort(ihaa)
for ii in ihaa:
    story = haa['story'][ii]
    if len(story) < 40 and story[-1].ismumeric():
        try:
            dd = '2023-' + story.split('.')[-1]+'-'+story.split('.')[-2][-2:].replace('-','').strip().zfill(2)
        except:
            dd = ''
    else:
        dd = ''
    newrow = [dd, haa['name'][ii], haa['age'][ii], haa['from'][ii],

    ##
# except Exception as e:
# print('war23_haaretz_kidnapped.py failed')
# a = os.system('echo "war23_haaretz_kidnapped.py failed" >> code/errors.log')
# b = os.system(f'echo "{e}" >> code/errors.log')
