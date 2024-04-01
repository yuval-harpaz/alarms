import pandas as pd
import os
# import Levenshtein
import numpy as np
import re


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

df = pd.read_csv('data/oct_7_9.csv')
# locs = ['בארי','נתיב העשרה','נחל עוז','נירים','ניר עוז','שדרות','כפר עזה','עלומים','רעים','כיסופים','חולית','אופקים']
##
issoldier = df['citizenGroup'].str.contains('צה"ל')
isinside = df['location'] == df['residence']
iscitizen = df['category'] == 'אזרחים וכיתות כוננות'
cg = df['citizenGroup'].values
cg[issoldier & iscitizen] = 'צה"ל: חייל בחופשה'
df['citizenGroup'] = cg
res = df['residence'].values
foreign = df['citizenGroup'] == 'אזרחים זרים'
res[foreign] = df['location'][foreign]
df['residence'] = res


locu = np.unique(df['residence'])
rows = []
for ii in range(len(locu)):
    rows.append([locu[ii], np.sum(df['residence'] == locu[ii])])
toll = pd.DataFrame(rows, columns=['ישוב', 'הרוגים'])

group = np.sort(np.unique(df['citizenGroup']))
for ii in range(len(locu)):
    isloc = df['residence'] == toll['ישוב'][ii]
    toll.at[ii, 'ביישוב'] = np.sum(isloc & isinside)
    inside = isloc
    tot = np.sum(isloc)
    for jj in range(len(group)):
        n = np.sum(isloc & (df['citizenGroup'] == group[jj]))
        toll.at[ii, group[jj]] = n
    # np.sum(isloc & isinside)
toll = toll.sort_values('הרוגים', ignore_index=True, ascending=False)
toll.to_csv('/home/innereye/Documents/groups.csv', index=False)
## אזרחים וכיתות כוננות
locuu = np.unique([x for x in df['location'].values if 'ירי בשוגג' not in x])
locuu = locuu[locuu != 'עזה']
cat = ['']*len(locuu)
cat[np.where(locuu =='פרי גן')[0][0]] = 'residential'
cat[np.where(locuu =='כוחלה')[0][0]] = 'residential'
cat = np.array(cat, str)
for ii in range(len(cat)):
    if 'מוצב' in locuu[ii] or 'מחנה' in locuu[ii]:
        cat[ii] = 'army'
    elif locuu[ii] in df['residence'].values:
        cat[ii] = 'residential'
    elif locuu[ii] in ['חוף זיקים','מסיבת פסיידאק','פסטיבל נובה']:
        cat[ii] = 'camping'
    else:
        cat[ii] = 'road'

for army in ['עמדה 91', 'מעבר ארז', 'מש"א ארז', 'מו"פ דרום']:
    cat[np.where(locuu == army)[0][0]] = 'army'

dfc = pd.DataFrame(columns=['loc', 'cat'])
dfc['loc'] = locuu
dfc['cat'] = cat
# dfc = df[df['category'] == 'אזרחים וכיתות כוננות']
##
cats = np.empty(len(df), dtype="<U11")
for icat in range(len(cats)):
    if df['comment'][icat] == 'מסיבת פסיידאק':
        cats[icat] = 'road'
    else:
        idx = np.where(dfc['loc'] == df['location'][icat])[0]
        if len(idx) == 1:
            cats[icat] = dfc['cat'].values[idx[0]]
##
summary = pd.DataFrame(columns=['cat', 'total', 'soldiers'])
summary['cat'] = ['residential', 'army', 'camping', 'road', '']
issoldier = df['category'].values == 'חיילים'
for ii in range(5):
    iscat = cats == summary['cat'][ii]
    summary.at[ii, 'total'] = np.sum(iscat)
    summary.at[ii, 'soldiers'] = np.sum(iscat & issoldier)
    if ii < 4:
        df[iscat & issoldier].to_csv('../Documents/'+summary['cat'][ii]+'.csv', index=False)
    else:
        df[iscat].to_csv('../Documents/not_included.csv', index=False)

ismig = df['location'].str.contains('מיגונ').to_numpy()

df[ismig].to_csv('../Documents/migunit.csv', index=False)
summary.to_csv('../Documents/summary.csv', index=False)
##
# fam =


##
first = df['fullName'].str.strip().str.split(' ')
first =[x[-1].replace('(','').replace(')','') for x in first]
first = np.array(first)
fu = np.unique(first)
count = []
for name in fu:
    count.append(np.sum(first == name))
names = pd.DataFrame(fu, columns = ['name'])
names['count'] = count
names = names.sort_values(['count', 'name'], ascending=[False, True], ignore_index=True)
names.to_csv('../Documents/names.csv', index=False)
## issue with map_row
# haa = pd.read_csv('data/deaths_haaretz+.csv')
# got_row = ~np.isnan(haa['map_row'].values)
# dup = []
# for ii in np.where(got_row)[0]:
#     if sum(haa['map_row'] == haa['map_row'][ii]) > 1:
#     dup.append(haa['map_row'][ii])
#  np.unique(dup)

## families
last = df['fullName'].str.split(' ')
last =[x[0] for x in last]
last = np.array(last)
lu = np.unique(last)
fams = []
for ll in lu:
    dfn = df[last == ll]
    ru = np.unique(dfn['residence'])
    for rr in ru:
        idx = dfn['residence'] == rr
        if np.sum(idx) > 1:
            fams.append(dfn[idx])
family = pd.concat(fams)
family.to_csv('../Documents/family.csv', index=False)