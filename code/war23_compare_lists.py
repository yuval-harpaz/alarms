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
ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0',' ')
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
erry = [x for x in range(len(ynet)) if x not in found_idf[:,1]]
erry = np.array(err)[ynet['דרגה'].values[err] == 'חייל']
soldier = np.unique(idf['rank'])
drg = np.unique([x for x in ynet['דרגה'].values if type(x) == str])
for dy in drg:
    if dy.split(' ')[0].strip() not in soldier:
        print(dy)

print(log)

##
df = idf.copy()
for ii in range(len(idf)):
    identifier = '|'.join([idf['name'][ii], str(idf['age'][ii]), idf['from'][ii]])
    if found_idf[ii, 2] > -1:
        df.at[ii, 'haaretz'] = haa['story'][found_idf[ii, 2]]
        identifier += ';'+'|'.join([haa['name'][found_idf[ii, 2]], haa['age'][found_idf[ii, 2]], haa['from'][found_idf[ii, 2]]])
    else:
        df.at[ii, 'haaretz'] = ''
        identifier += ';'
    if found_idf[ii, 1] > -1:
        df.at[ii, 'ynet'] = ynet['מידע על המוות'][found_idf[ii, 1]]
        f = ynet['שם פרטי'][found_idf[ii, 1]]
        df.at[ii, 'first'] = f
        l = ynet['שם משפחה'][found_idf[ii, 1]]
        df.at[ii, 'last'] = l
        identifier += ';' + '|'.join(
            [f+' '+l, ynet['גיל'][found_idf[ii, 1]], ynet['מקום מגורים'][found_idf[ii, 1]]])
    else:
        df.at[ii, 'ynet'] = ''
        df.at[ii, 'first'] = idf['name'][ii].split(' ')[0]
        df.at[ii, 'last'] = ' '.join(idf['name'][ii].split(' ')[1:])
        identifier += ';'
    df.at[ii, 'identifier'] = identifier
df['status'] = 'חייל'
##
ihaa = [x for x in range(len(haa)) if x not in found_idf[:,2]]
ihaa = np.sort(ihaa)
for ii in ihaa:
    story = haa['story'][ii]
    if type(story) != float and len(story) < 40 and story[-1].isdigit():
        try:
            dd = '2023-' + story.split('.')[-1]+'-'+story.split('.')[-2][-2:].replace('-','').strip().zfill(2)
        except:
            dd = ''
    else:
        dd = ''
    idt = ';'+'|'.join([haa['name'][ii], str(haa['age'][ii]).replace('nan',''), haa['from'][ii]])+';'
    newrow = [dd, haa['name'][ii],'', '', '', haa['age'][ii], haa['from'][ii], '', haa['story'][ii],'', '', '', idt, haa['status'][ii]]
    df.loc[len(df)] = newrow

df.to_csv('data/deaths.csv', index=False)
##
df = pd.read_csv('data/deaths.csv')
yd = []
for yy in range(len(ynet)):
    f = ynet['שם פרטי'][yy]
    l = ynet['שם משפחה'][yy]
    idt = '|'.join([f + ' ' + l,
                    str(ynet['גיל'][yy]).replace('nan',''),
                    str(ynet['מקום מגורים'][yy]).replace('nan','')])
    yd.append(idt)
yd = np.array(yd)
for row in np.where(df['first'].isnull().values)[0]:
    hd = df['identifier'][row].split(';')[1]
    for rem in ['קיבוץ ', 'מושב ']:
        hd = hd.replace(rem, '')
    do_from = False
    if df['status'][row] == 'שוטר':
        hd = hd[hd.index(' ')+1:]
        if hd[-1] == '-':
            hd = hd[:-2]
            do_from = True
            dist = [Levenshtein.distance(hd, '|'.join(x.split('|')[:2])) for x in yd]
        else:
            dist = [Levenshtein.distance(hd, x) for x in yd]
    else:
        dist = [Levenshtein.distance(hd, x) for x in yd]
    imin = np.argmin(dist)
    vmin = dist[imin]
    if vmin < 3:
        ids = df['identifier'][row].split(';')
        ids[2] = yd[imin]
        df.at[row, 'identifier'] = ';'.join(ids)
        df.at[row, 'first'] = ynet['שם פרטי'][imin]
        df.at[row, 'last'] = ynet['שם משפחה'][imin]
        df.at[row, 'ynet'] = ynet['מידע על המוות'][imin]
        if do_from:
            df.at[row, 'from'] = ynet['מקום מגורים'][imin]

#
indf = [x[2] for x in df['identifier'].str.split(';').values if len(x[2]) > 0]
indf = np.array(indf)
leftover = [x for x in range(len(yd)) if yd[x] not in indf]
print(len(leftover))
df.to_csv('data/tmp_deaths.csv', index=False)
ynetl = ynet.iloc[leftover]
ynetl.to_csv('data/tmp_leftover.csv', index=False)
##
yparts = []
for yy in range(len(leftover)):
    yparts.append([ynet['שם פרטי'][yy],
                  ynet['שם משפחה'][yy],
                  str(ynet['גיל'][yy]).replace('nan', ''),
                  str(ynet['מקום מגורים'][yy]).replace('nan', '')])
    yparts[-1] = [x for x in yparts[-1] if len(x) > 0]
##
for row in np.where(df['first'].isnull().values)[0]:
    hd = df['identifier'][row].split(';')[1]
    hd = [x.split(' ') for x in hd.split('|')]
    hparts = []
    for p in hd:
        hparts.extend(p)
    score = []
    for iy in range(len(yparts)):
        scr = 0
        for yp in yparts[iy]:
            scr += (yp in hparts)
        score.append(scr)
    if max(score) > 2:
        imax = np.argmax(score)
        print(df['identifier'][row].split(';')[1] + ' >> ' + '|'.join(yparts[imax]))

##


#
#     for rem in ['קיבוץ ', 'מושב ']:
#         hd = hd.replace(rem, '')
#     do_from = False
#     if df['status'][row] == 'שוטר':
#         hd = hd[hd.index(' ')+1:]
#         if hd[-1] == '-':
#             hd = hd[:-2]
#             do_from = True
#             dist = [Levenshtein.distance(hd, '|'.join(x.split('|')[:2])) for x in yd]
#         else:
#             dist = [Levenshtein.distance(hd, x) for x in yd]
#     else:
#         dist = [Levenshtein.distance(hd, x) for x in yd]
#     imin = np.argmin(dist)
#     vmin = dist[imin]
#     if vmin < 3:
#         ids = df['identifier'][row].split(';')
#         ids[2] = yd[imin]
#         df.at[row, 'identifier'] = ';'.join(ids)
#         df.at[row, 'first'] = ynet['שם פרטי'][imin]
#         df.at[row, 'last'] = ynet['שם משפחה'][imin]
#         df.at[row, 'ynet'] = ynet['מידע על המוות'][imin]
#         if do_from:
#             df.at[row, 'from'] = ynet['מקום מגורים'][imin]
#
# #
# indf = [x[2] for x in df['identifier'].str.split(';').values if len(x[2]) > 0]
# indf = np.array(indf)
# leftover = [x for x in range(len(yd)) if yd[x] not in indf]

##
# except Exception as e:
# print('war23_haaretz_kidnapped.py failed')
# a = os.system('echo "war23_haaretz_kidnapped.py failed" >> code/errors.log')
# b = os.system(f'echo "{e}" >> code/errors.log')
