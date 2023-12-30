import pandas as pd
import os
import Levenshtein
import numpy as np


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True


haa = pd.read_csv('data/deaths_haaretz.csv').iloc[::-1]
haa.reset_index(inplace=True, drop=True)
ynet = pd.read_csv('data/ynetlist.csv')
ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0',' ')
idf = pd.read_csv('data/deaths_idf.csv')
df = pd.read_csv('data/deaths_haaretz+.csv')
##
new = haa.iloc[np.where(haa['name'].str.contains(df['name'][len(df)-1]))[0][0]+1:]
new.reset_index(inplace=True, drop=True)
mil = r'\([^)]*מיל[^)]*\)'
for ii in range(len(new)):
    if new['status'][ii] == 'שוטר':
        rank = new['name'][ii].split(' ')[0]
        name = ' '.join(new['name'][ii].split(' ')[1:])
    elif new['status'][ii] == 'חייל':
        nm = new['name'][ii]
        if re.search(mil, nm):
            rank = nm[:nm.index(')')+1]
            name = nm[nm.index(')')+2:]
        else:
            rank = nm.split(' ')[0]
            name = ' '.join(new['name'][ii].split(' ')[1:])
    else:
        name = new['name'][ii]
        rank = np.nan
    story = str(new['story'][ii])
    if 'נפל ' in story or 'נרצח ' in story or 'נפטר ' in story:
        gender = 'M'
    elif 'נפלה ' in story or 'נרצחה ' in story or 'נפטרה ' in story:
        gender = 'F'
    else:
        gender = ''
    status = new['status'][ii]
    idf_row = np.nan
    death_date = ''
    if status == 'חייל':
        idf_row = np.where(idf['name'].str.contains(name))[0]
        if len(idf_row) == 1:
            idf_row = idf_row[0]
            death_date = idf['death_date'][idf_row]
    else:
        if len(story) > 4 and story[-1:].isdigit():
            dd = story.split(' ')[-1]
            if '-' in dd:
                dd = dd[dd.index('-')+1:].strip()
            if dd.split('.')[0].isdigit() and dd.split('.')[1].isdigit():
                death_date = '2023-'+dd.split('.')[1].zfill(2)+'-'+dd.split('.')[0].zfill(2)
    story = story.replace('nan', '')
    row = [name, rank, new['age'][ii], gender, new['from'][ii], status, story, idf_row, death_date]
    df.loc[len(df)] = row



##
df.to_csv('data/deaths_haaretz+.csv', index=False)
##
# darga = np.unique(idf['rank'])
# darga = np.unique([x.split(' ')[0] for x in darga])
# darga = list(np.unique([x.replace('"','״') for x in darga]))
# police = haa[haa['status'] == 'שוטר']['name'].values
# police = [p.split(' ')[0] for p in police]
# police = list(np.unique(police))
# darga = np.unique(darga + police)
#
#
# # deaths = pd.read_csv('data/deaths.csv')
# ##  Check idf
# equal = [idf['name'].values[ii] == deaths['name'][ii] for ii in range(len(idf))]
# update = deaths.iloc[np.where(equal)[0]].copy()
# # update.reset_index(drop=True, inplace=True)
# if all(equal):
#     update = pd.concat([update, deaths.iloc[len(idf):]], ignore_index=True)
# else:
#     new = np.where(~np.array(equal))[0]
#     for inew in new:
#         for col in idf.columns:
#             update.at[inew, col.replace('story','idf')] = idf.iloc[inew][col]
#         # name = update['name'][inew]
#     update = pd.concat([update, deaths.iloc[new[0]:]], ignore_index=True)
# ##  check haaretz
# darga = np.unique(idf['rank'])
# darga = np.unique([x.split(' ')[0] for x in darga])
# darga = list(np.unique([x.replace('"','״') for x in darga]))
# for drg in darga:
#     if '״' in drg:
#         darga.append(drg.replace('״', '"'))
# storyh = update['haaretz'].values
# for ii in range(len(haa)):
#     isnew = False
#     if haa['story'][ii] not in storyh:
#         isnew = True
#     idh = '|'.join([haa['name'][ii], str(haa['age'][ii]), str(haa['from'][ii])])
#     ids = update['identifier'].values.astype(str)
#     match = np.where([idh in x for x in ids])
#     if len(match) == 0:
#         isnew = True
#     elif len(match) > 1:
#         print('XXXXXXX')
#         print(f'{ii} {haa["name"][ii]} {len(match)} matches')
#         print('XXXXXXX')
#         raise Exception(f'{ii} {haa["name"][ii]} {len(match)} matches')
#     else:
#         pass  # no news
#     if isnew:
#         nameh = haa["name"][ii]
#         for mil in ["(במיל')", "(מיל')", "(מיל׳)", "(במיל׳)"]:
#             if mil in nameh:
#                 nameh = nameh[nameh.index(mil)+len(mil):].strip()
#         for drg in darga:
#             nameh = nameh.replace(drg, '').strip()
#         row_idf = np.where(idf['name'].str.contains(nameh))[0]
#         if len(row_idf) == 1:
#             row_idf = int(row_idf)
#             idi = '|'.join([idf['name'][row_idf], str(idf['age'][row_idf]), str(idf['from'][row_idf])])
#             if update['haaretz'].isnull()[row_idf]:
#                 update.at[row_idf, 'haaretz'] = haa['story'][ii]
#                 update.at[row_idf, 'status'] = haa['status'][ii]
#                 update.at[row_idf, 'identifier'] = idi+';'+idh+';'
#             print(f'added from haaretz {ii} {haa["name"][ii]}')
#         elif len(row_idf) > 1:
#             raise Exception('too many fits')
#         else:
#             already = []
#             for x in range(len(update)):
#                 id0 = update['identifier'][x]
#                 if type(id0) == str and idh in id0:
#                     already.append(x)
#             if len(already) == 0:
#                 # already = [x for x in range(len(update)) if and(type(idh in update['identifier'][x]]
#                 next = len(update)
#                 update.at[next, 'name'] = haa['name'][ii]
#                 update.at[next, 'age'] = haa['age'][ii]
#                 update.at[next, 'from'] = haa['from'][ii]
#                 update.at[next, 'haaretz'] = haa['story'][ii]
#                 update.at[next, 'status'] = haa['status'][ii]
#                 update.at[next, 'identifier'] = ';' + idh + ';'
#                 print(f'added new line from haaretz {ii} {haa["name"][ii]}')
#             elif len(already) == 1:
#                 print('a')
#             else:
#                 raise Exception('too many fits for '+nameh)
#
# update.to_csv('data/deaths.csv', index=False)
# # TODO: sanity checks (no duplicates), ynet
#
#
# changed = False
# if len(idf) >= to_fill:
#     ynet = pd.read_csv('data/ynetlist.csv')
#     yd = []
#     for iy in range(len(ynet)):
#         yd.append('|'.join([ynet[ynet.columns[5]][iy] + ' ' + ynet[ynet.columns[6]][iy],
#                        str(ynet['גיל'][iy]), str(ynet['מקום מגורים'][iy])]))
#     otef = '|'.join(['זיקים', 'נתיב העשרה', 'כפר עזה', 'נחל עוז', 'שדרות', 'בארי', 'כיסופים', 'מפלסים'])
#     for ii in range(to_fill, len(idf)):
#         st = idf['story'][ii]
#         yy = ''
#         ff = ''
#         id = '|'.join([idf['name'][ii], str(idf['age'][ii]), str(idf['from'][ii])])
#         distance = [Levenshtein.distance(id, x) for x in yd]
#         if min(distance) < 3:
#             yrow = np.argmin(distance)
#             yy = ynet['מידע על המוות'][yrow]
#         if (type(re.search(otef, yy)) == re.Match) or \
#             (type(re.search(otef, st)) == re.Match):
#             ff = 'עוטף עזה'
#         elif (type(re.search(r'נפל בקרב.+רצוע', yy)) == re.Match) or \
#              (type(re.search(r'נפל בקרב.+רצוע', st)) == re.Match):
#             ff = 'עזה'
#         elif 'לבנון' in yy or 'לבנון' in st:
#             ff = 'לבנון'
#         elif 'נרצח' in yy or 'נרצח' in st:
#             ff = 'נרצח כאזרח'
#         elif idf['death_date'][ii] > '2023-10-30' and ('הרצועה' in st or 'רצועת עזה' in st):
#             ff = 'עזה'
#         if len(yy) > 0 or len(ff) > 0:
#             changed = True
#         front.loc[ii] = [idf['name'][ii], st, yy, ff]
##
    # n_parts = np.zeros(len(update))
    # for name_part in haa['name'][ii].split(' '):
    #     n_parts += update['identifier'].str.contains(name_part)

##
# found_idf = np.zeros((len(idf), 3), int)
# found_idf[:, 1:] = -1
# found_idf[:, 0] = np.arange(len(idf))
# tbl = 0
# for table in [ynet, haa]:
#     tbl += 1
#     if tbl == 1:
#         age = table['גיל'].values
#         fro = table['מקום מגורים'].values
#         val = []
#         for jj in range(len(table)):
#             val.append(table['שם פרטי'][jj]+' '+table['שם משפחה'][jj])
#     else:
#         val = table['name'].str.replace('׳', "'").values
#         age = table['age'].values
#         fro = table['from'].values
#     for ii in range(len(idf)):
#         name = idf['name'][ii]
#         for jj in range(len(val)):
#             agefit = age[jj] == str(idf['age'][ii])
#             if name in val[jj]:
#                 if agefit:
#                     found_idf[ii, tbl] = jj
#                 else:
#                     print(f'{name} ages: {age[jj]} {idf["age"][ii]}')
#                     if type(fro[jj]) == str and Levenshtein.distance(fro[jj], idf['from'][ii]) < 2:
#                         found_idf[ii, tbl] = jj
#                     else:
#                         print(f'{name} locs: {fro[jj]} {idf["from"][ii]}')
#             else:
#                 fit = 0
#                 for part in name.split(' '):
#                     if part in val[jj]:
#                         fit += 1
#                 if fit > 1 and agefit:
#                     found_idf[ii, tbl] = jj
#                 elif name.split(' ')[0] in val[jj] and agefit:
#                     dist = []
#                     for nm in name.split(' ')[1:]:
#                         for vl in val[jj].split(' '):
#                             dist.append(Levenshtein.distance(nm,vl))
#                     if min(dist) < 2:
#                         found_idf[ii, tbl] = jj
# found_idf[np.where(idf['name'].str.contains('עלים'))[0], 2] = np.where(haa['name'].str.contains('עלים'))[0][0]
# found_idf[np.where(idf['name'].str.contains('יהונתן אהרן שטיינברג'))[0], 2] = np.where(haa['name'].str.contains('יהונתן אהרן שטיינברג'))[0][0]
# ormizrahi = np.where(idf['name'].str.contains('אור מזרחי'))
# print(np.sum(found_idf == -1, 0))
#
# ##
# log = 'idf not in haaretz: '+', '.join(idf['name'][found_idf[:,2] == -1].values)+'\n'
# log = log + 'idf not in ynet: '+', '.join(idf['name'][found_idf[:,1] == -1].values)+'\n'
# err = [x for x in range(len(haa)) if x not in found_idf[:,2]]
# err = np.array(err)[haa['status'].values[err] == 'חייל']
# log = log + 'haaretz not in idf:' + ', '.join(haa['name'][err]) + '\n'
# erry = [x for x in range(len(ynet)) if x not in found_idf[:,1]]
# erry = np.array(err)[ynet['דרגה'].values[err] == 'חייל']
# soldier = np.unique(idf['rank'])
# drg = np.unique([x for x in ynet['דרגה'].values if type(x) == str])
# for dy in drg:
#     if dy.split(' ')[0].strip() not in soldier:
#         print(dy)
#
# print(log)
#
# ##
# df = idf.copy()
# for ii in range(len(idf)):
#     identifier = '|'.join([idf['name'][ii], str(idf['age'][ii]), idf['from'][ii]])
#     if found_idf[ii, 2] > -1:
#         df.at[ii, 'haaretz'] = haa['story'][found_idf[ii, 2]]
#         identifier += ';'+'|'.join([haa['name'][found_idf[ii, 2]], haa['age'][found_idf[ii, 2]], haa['from'][found_idf[ii, 2]]])
#     else:
#         df.at[ii, 'haaretz'] = ''
#         identifier += ';'
#     if found_idf[ii, 1] > -1:
#         df.at[ii, 'ynet'] = ynet['מידע על המוות'][found_idf[ii, 1]]
#         f = ynet['שם פרטי'][found_idf[ii, 1]]
#         df.at[ii, 'first'] = f
#         l = ynet['שם משפחה'][found_idf[ii, 1]]
#         df.at[ii, 'last'] = l
#         identifier += ';' + '|'.join(
#             [f+' '+l, ynet['גיל'][found_idf[ii, 1]], ynet['מקום מגורים'][found_idf[ii, 1]]])
#     else:
#         df.at[ii, 'ynet'] = ''
#         df.at[ii, 'first'] = idf['name'][ii].split(' ')[0]
#         df.at[ii, 'last'] = ' '.join(idf['name'][ii].split(' ')[1:])
#         identifier += ';'
#     df.at[ii, 'identifier'] = identifier
# df['status'] = 'חייל'
# ##
# ihaa = [x for x in range(len(haa)) if x not in found_idf[:,2]]
# ihaa = np.sort(ihaa)
# for ii in ihaa:
#     story = haa['story'][ii]
#     if type(story) != float and len(story) < 40 and story[-1].isdigit():
#         try:
#             dd = '2023-' + story.split('.')[-1]+'-'+story.split('.')[-2][-2:].replace('-','').strip().zfill(2)
#         except:
#             dd = ''
#     else:
#         dd = ''
#     idt = ';'+'|'.join([haa['name'][ii], str(haa['age'][ii]).replace('nan',''), haa['from'][ii]])+';'
#     newrow = [dd, haa['name'][ii],'', '', '', haa['age'][ii], haa['from'][ii], '', haa['story'][ii],'', '', '', idt, haa['status'][ii]]
#     df.loc[len(df)] = newrow
#
# df.to_csv('data/deaths.csv', index=False)
# ##
# df = pd.read_csv('data/deaths.csv')
# yd = []
# for yy in range(len(ynet)):
#     f = ynet['שם פרטי'][yy]
#     l = ynet['שם משפחה'][yy]
#     idt = '|'.join([f + ' ' + l,
#                     str(ynet['גיל'][yy]).replace('nan',''),
#                     str(ynet['מקום מגורים'][yy]).replace('nan','')])
#     yd.append(idt)
# yd = np.array(yd)
# for row in np.where(df['first'].isnull().values)[0]:
#     hd = df['identifier'][row].split(';')[1]
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
# print(len(leftover))
# df.to_csv('data/tmp_deaths.csv', index=False)
# ynetl = ynet.iloc[leftover]
# ynetl.to_csv('data/tmp_leftover.csv', index=False)
# ##
# yparts = []
# for yy in range(len(leftover)):
#     yparts.append([ynet['שם פרטי'][yy],
#                   ynet['שם משפחה'][yy],
#                   str(ynet['גיל'][yy]).replace('nan', ''),
#                   str(ynet['מקום מגורים'][yy]).replace('nan', '')])
#     yparts[-1] = [x for x in yparts[-1] if len(x) > 0]
# ##
# for row in np.where(df['first'].isnull().values)[0]:
#     hd = df['identifier'][row].split(';')[1]
#     hd = [x.split(' ') for x in hd.split('|')]
#     hparts = []
#     for p in hd:
#         hparts.extend(p)
#     score = []
#     for iy in range(len(yparts)):
#         scr = 0
#         for yp in yparts[iy]:
#             scr += (yp in hparts)
#         score.append(scr)
#     if max(score) > 2:
#         imax = np.argmax(score)
#         print(df['identifier'][row].split(';')[1] + ' >> ' + '|'.join(yparts[imax]))
#
# ##
#
#
# #
# #     for rem in ['קיבוץ ', 'מושב ']:
# #         hd = hd.replace(rem, '')
# #     do_from = False
# #     if df['status'][row] == 'שוטר':
# #         hd = hd[hd.index(' ')+1:]
# #         if hd[-1] == '-':
# #             hd = hd[:-2]
# #             do_from = True
# #             dist = [Levenshtein.distance(hd, '|'.join(x.split('|')[:2])) for x in yd]
# #         else:
# #             dist = [Levenshtein.distance(hd, x) for x in yd]
# #     else:
# #         dist = [Levenshtein.distance(hd, x) for x in yd]
# #     imin = np.argmin(dist)
# #     vmin = dist[imin]
# #     if vmin < 3:
# #         ids = df['identifier'][row].split(';')
# #         ids[2] = yd[imin]
# #         df.at[row, 'identifier'] = ';'.join(ids)
# #         df.at[row, 'first'] = ynet['שם פרטי'][imin]
# #         df.at[row, 'last'] = ynet['שם משפחה'][imin]
# #         df.at[row, 'ynet'] = ynet['מידע על המוות'][imin]
# #         if do_from:
# #             df.at[row, 'from'] = ynet['מקום מגורים'][imin]
# #
# # #
# # indf = [x[2] for x in df['identifier'].str.split(';').values if len(x[2]) > 0]
# # indf = np.array(indf)
# # leftover = [x for x in range(len(yd)) if yd[x] not in indf]
#
# ##
# # except Exception as e:
# # print('war23_haaretz_kidnapped.py failed')
# # a = os.system('echo "war23_haaretz_kidnapped.py failed" >> code/errors.log')
# # b = os.system(f'echo "{e}" >> code/errors.log')
