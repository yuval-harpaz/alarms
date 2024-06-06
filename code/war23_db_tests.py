import pandas as pd
import os
import numpy as np
import unittest
import sys
sys.path.append('code')

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

# data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
data = pd.read_csv('data/oct7database.csv')
omi = pd.read_csv('/home/innereye/Documents/oct7database - omissions.csv')
##
''' TODO
check that middle names and nicknames are present for both languages
check that all parts of a name are present in the corresponding url
'''
def duplicates(pid, names):
    dup = pd.DataFrame(columns=['idx', 'pid', 'name'])
    for ii in range(len(names)):
        row = np.where(names == names[ii])[0]
        row = row[row != ii]
        if len(row) == 1:
            dup.loc[len(dup)] = [ii, pid[row[0]], names[ii]]
        elif len(row) > 1:
            raise Exception('more than 2 '+names[ii])
    return dup


##
class TestDuplicates(unittest.TestCase):
    def duplicate_pid(self):
        pid = data['pid'].values
        # dup_df = duplicates(pid, pid)
        dup_pid = duplicates(pid, pid)
        duplicates_length = len(dup_pid)
        if duplicates_length > 0:
            print(f'PID Duplicates!!!! {np.unique(dup_pid["pid"])}'.replace('[', '').replace(']', ''))
        self.assertEqual(duplicates_length, 0)

    def duplicate_heb(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            names.append(data['שם פרטי'][ii] + ' ' + data['שם משפחה'][ii])
        names = np.array(names)
        dup_heb = duplicates(pid, names)
        dup_names = np.unique(dup_heb['name'])
        okay_dup = np.sort(['אור מזרחי', 'דניאל כהן', 'עמית כהן', 'רותם לוי', 'לידור לוי'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('Hebrew Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_heb.to_csv('/home/innereye/Documents/dup.csv', index=False)
            print(' See: Documents/dup.csv')
        self.assertEqual(duplicates_length, len(okay_dup))

    def duplicate_eng(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            names.append(data['first name'][ii] + ' ' + data['last name'][ii])
        names = np.array(names)
        dup_eng = duplicates(pid, names)
        dup_names = np.unique(dup_eng['name'])
        okay_dup = np.sort(['Or Mizrahi', 'Daniel Cohen', 'Amit Cohen', 'Ohad Cohen', 'Rotem Levi'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('English Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_eng.to_csv('/home/innereye/Documents/dup_eng.csv', index=False)
            print(' See: Documents/dup_eng.csv')
        self.assertEqual(duplicates_length, len(okay_dup))

    def duplicate_url(self):
        dfurl = data[~data['הנצחה'].isnull()]
        pid_url = dfurl['pid'].values
        dup_url = duplicates(pid_url, dfurl['הנצחה'].values)
        duplicates_length = len(dup_url)
        if duplicates_length > 0:
            du = np.unique([x.split('/')[-1] for x in dup_url['name']])
            print(f'URL Duplicates!!!! {du}'.replace('[', '').replace(']', ''))
        self.assertEqual(duplicates_length, 0)


class TestOmissions(unittest.TestCase):
    def not_dropped(self):
        pid = data['pid'].values
        nd = [x for x in omi['pid'] if x in pid]
        n_not_dropped = len(nd)
        if n_not_dropped > 0:
            print(f'Not omitted!!!! {nd}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_not_dropped, 0)

    def dropped(self):
        pid = data['pid'].values
        pid_okay = omi['duplicate'][~omi['duplicate'].isnull()].values
        dpd = [x for x in pid_okay if x not in pid]
        n_dropped = len(dpd)
        if n_dropped > 0:
            print(f'Omitted a valid PID!!!! {dpd}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_dropped, 0)

    def all_acounted(self):
            pid = data['pid'].values
            pid_all = np.unique(list(omi['pid']) + list(pid))
            try:
                json = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
            except:
                raise Exception('no internet?')
            pid_json = json['pid'].values
            unaccounted = [x for x in pid_json if x not in pid_all]
            n_missing = len(unaccounted)
            if n_missing > 0:
                print(f'Unaccounted for PID!!!! {unaccounted}'.replace('[', '').replace(']', ''))
            self.assertEqual(n_missing, 0)


map79 = pd.read_csv('data/oct_7_9.csv')


class Test79(unittest.TestCase):
    def extras79(self):
        pid = data['pid'].values
        ext = [x for x in map79['pid'] if x not in pid]
        n_extra = len(ext)
        if n_extra > 0:
            print(f'OCT_7_9 PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def unique_pid79(self):
        pid79 = map79['pid'].values
        len_unique = len(pid79) - len(np.unique(pid79))
        if len_unique > 0:
            dup79 = np.unique([x for x in pid79 if np.sum(pid79 == x) > 1])
            print(f'OCT_7_9 PID Not Unique!!!! {dup79}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)


haa = pd.read_csv('data/deaths_haaretz+.csv')
class TestHaa(unittest.TestCase):
    def extras_haa(self):
        pid = data['pid'].values
        ext = [x for x in haa['pid'] if x not in pid]
        ext = np.array(ext)
        ext = np.unique(ext[~np.isnan(ext)]).astype(int)
        n_extra = len(ext)
        if n_extra > 0:
            print(f'haaretz+ PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def missing_haa(self):  # TODO: add kidnapped
        pid = data['pid'].values
        pid_haa = haa['pid'].values
        missing = [x for x in pid if x not in pid_haa]
        missing = np.array(missing)
        missing = np.unique(missing[~np.isnan(missing)]).astype(int)
        n_extra = len(missing)
        if n_extra > 0:
            print(f'haaretz+ PID Not in DB!!!! {missing}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)



    def unique_haa(self):
        pid_haa = haa['pid'].values
        pid_haa = pid_haa[~np.isnan(pid_haa)]
        len_unique = len(pid_haa) - len(np.unique(pid_haa))
        if len_unique > 0:
            dup_haa = np.unique([x for x in pid_haa if np.sum(pid_haa == x) > 1])
            print(f'haartz+ PID Not Unique!!!! {dup_haa}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)

##
oct7db_results = unittest.TestResult()
oct7suite = unittest.TestSuite(tests=[TestDuplicates('duplicate_pid'),
                                      TestDuplicates('duplicate_heb'),
                                      TestDuplicates('duplicate_eng'),
                                      TestDuplicates('duplicate_url'),
                                      TestOmissions('not_dropped'),
                                      TestOmissions('dropped'),
                                      TestOmissions('all_acounted'),
                                      Test79('extras79'),
                                      Test79('unique_pid79'),
                                      TestHaa('extras_haa'),
                                      TestHaa('unique_haa'),
                                      # TestHaa('missing_haa'),  kidnapped missing
                                      ]
                               )

oct7suite.run(oct7db_results)
print('XXXXXXXXXXXXXXXXXXXXXXXX')
print('N tests failed = '+str(len(oct7db_results.failures))+'/'+str(oct7db_results.testsRun))  #+\
      # ' including '+str(len(oct7db_results.expectedFailures))+' expected failures')
print('N tests with bugs = '+str(len(oct7db_results.errors))+'/'+str(oct7db_results.testsRun))
if len(oct7db_results.failures) > 0:
    print('failed:')
    for fl in oct7db_results.failures:
        for msg in fl:
            print(msg)
if len(oct7db_results.errors) > 0:
    print('Errors:')
    print('-------')
    for err in oct7db_results.errors:
        for msg in err:
            print(msg)
print('XXXXXXXXXXXXXXXXXXXXXXXX')

##
# map7 = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
# map = pd.read_csv('data/oct_7_9.csv')
# cref = pd.read_csv('data/crossref.csv')
# # locs = pd.DataFrame(cref['oct_7_9_fullName'])
# names = pd.read_excel('/home/innereye/Documents/names.xlsx')
# df = pd.read_excel('/home/innereye/Documents/database.xlsx')
# btl = pd.read_excel('/home/innereye/Documents/btl_yael_netzer.xlsx')
# ## complete foreign names
# # df = map7.filter(['pid','name'], axis=1)
# # df = df.sort_values('pid', ignore_index=True)
# for ii in range(len(df)):
#     pid = df['pid'][ii]
#     icref = np.where(cref['oct7map_pid'] == pid)[0]
#     if len(icref) == 1:
#         icref = icref[0]
#         if type(df['שם פרטי'][ii]) != str:
#             name = cref['btl_name'][icref]
#             if type(name) == str:
#                 name = name.split('  ')
#                 if len(name) == 2:
#                     df.at[ii, 'שם משפחה'] = name[1]
#                 if ' ' in name[0]:
#                     first = name[0][:name[0].index(' ')]
#                     middle = name[0][name[0].index(' '):]
#                 else:
#                     first = name[0]
#                     middle = ''
#                 df.at[ii, 'שם פרטי'] = first
#                 df.at[ii, 'שם נוסף'] = middle
# for col in df.columns[1:]:
#     df[col] = df[col].str.strip()
# df.to_excel('/home/innereye/Documents/database.xlsx', index=False)
# ## fix status
# for ii in range(len(df)):
#     row = np.where(map7['pid'] == df['pid'][ii])[0][0]
#     df.at[ii, 'status'] = map7['status'][row]
#
# ## add soldiers and other empty
# # nobtl = np.where(cref['btl_id'] == 0)[0]
# # pidnobtl = cref['oct7map_pid'].values[nobtl]
# # nobtl = nobtl[pidnobtl > 0]
# # pidnobtl = pidnobtl[pidnobtl > 0]
# # rows = [np.where(df['pid'] == x)[0][0] for x in pidnobtl]
# ## split english
# rows = np.where(df['first name'].isnull())[0]
# for ii in rows:
#     name = df['name'][ii].split(' ')
#     df.at[ii, 'first name'] = name[0]
#     df.at[ii, 'last name'] = name[-1]
#     if len(name) > 2:
#         df.at[ii, 'middle name'] = ' '.join(name[1:-1])
#
# ## add oct_7_9
# map = pd.read_csv('data/oct_7_9.csv')
# included = []
# for ii in range(len(df)):
#     pid = df['pid'][ii]
#     icref = np.where(cref['oct7map_pid'] == pid)[0]
#     if len(icref) == 1:
#         icref = icref[0]
#         row = cref['oct_7_9_id'][icref]
#         included.append(row-1)
# notinc = [x for x in range(len(map)) if x not in included]
# new = pd.DataFrame(columns=df.columns)
# for ii in range(len(notinc)):
#     pid = 2000+ii+1
#     name = map['fullName'][notinc[ii]].split(' ')
#     # df.at[ii, 'first name'] = name[0]
#     firsth = name[-1]
#     lasth = name[0]
#     # df.at[ii, 'last name'] = name[-1]
#     if len(name) > 2:
#         middleh = ' '.join(name[1:-1])
#     else:
#         middleh = np.nan
#     name = map['eng'][notinc[ii]].split(' ')
#     # df.at[ii, 'first name'] = name[0]
#     firste = name[0]
#     laste = name[-1]
#     # df.at[ii, 'last name'] = name[-1]
#     if len(name) > 2:
#         middlee = ' '.join(name[1:-1])
#     else:
#         middlee = np.nan
#     newrow = [pid, map['fullName'][notinc[ii]], firste, laste, middlee, np.nan, firsth, lasth, middleh, np.nan, np.nan]
#     new.loc[len(new)] = newrow
# new.to_excel('/home/innereye/Documents/missing.xlsx', index=False)
# ## integrate new pid to rxisting lists
# db = pd.read_csv('/home/innereye/Documents/oct7database.csv')
# haa = pd.read_csv('/home/innereye/alarms/data/deaths_haaretz+.csv')
# cref = pd.read_csv('data/crossref.csv')
# map = pd.read_csv('data/oct_7_9.csv')
#
# pids = db['pid'].values
# for ii in range(len(cref)):
#     pid = cref['oct7map_pid'][ii]
#     if pid > 0:
#         map_row = cref['oct_7_9_id'][ii] - 1
#         map.at[map_row, 'pid'] = pid
# map.to_csv('data/oct_7_9.csv', index=False)
# ##
# for ii in range(len(map)):
#     pid = map['pid'][ii]
#     haa_row = np.where(haa['map_row'] == ii + 2)[0]
#     if len(haa_row) == 1:
#         haa.at[haa_row[0], 'pid'] = pid
# haa.to_csv('data/deaths_haaretz+.csv', index=False)
#
# idf = pd.read_csv('data/deaths_idf.csv')
# recent = haa.filter(['pid', 'name', 'rank', 'death_date'])
# recent = recent[recent['pid'].isnull()]
# for ii in recent.index:
#     idf_row = haa['idf_row'][ii] - 2
#     if ~np.isnan(idf_row):
#         name = idf['name'][idf_row]
#         recent.at[ii, 'idf_name'] = name
#         name = name.split(' ')
#     else:
#         name = haa['name'][ii].split(' ')
#     recent.at[ii, 'שם פרטי'] = name[0]
#     recent.at[ii, 'שם משפחה'] = name[-1]
#     if len(name) > 2:
#         middle = ' '.join(name[1:-1])
#         recent.at[ii, 'שם נוסף'] = middle
# recent.to_csv('/home/innereye/Documents/recent.csv', index=False)
# ##
# recent = pd.read_csv('/home/innereye/Documents/recent.csv')
# idf = pd.read_csv('data/tmp_idf_eng.csv')
# for ii in range(len(recent)):
#     namer = recent['name'][ii].split()
#     fit = []
#     for jj in range(len(idf)):
#         namei = idf['heb'][jj]
#         score = 0
#         for part in namer:
#             if part in namei:
#                 score += 1
#         fit.append(score)
#     cand = np.where(np.array(fit) > 1)[0]
#     if len(cand) == 1:
#         recent.at[ii, 'idf_eng'] = idf['eng'][cand[0]]
#     print(ii)
# ##
# recent = pd.read_csv('/home/innereye/Documents/recent_eng.csv')
# for ii in range(len(recent)):
#     name = recent['idf_eng'][ii]
#     if type(name) == str:
#         if '(res.)' in name:
#             name = name[name.index('(res.)') + 6:].strip()
#         elif 'class' in name.lower():
#             name = name[name.lower().index('class') + 5:].strip()
#         else:
#             rank = [x for x in ['sergeant', 'sergent', 'captain', 'lieutenant', 'major'] if x in name.lower()]
#             if len(rank) == 1:
#                 name = name[name.lower().index(rank[0]) + len(rank[0]):].strip()
#         name = name.split(' ')
#         recent.at[ii, 'first name'] = name[0]
#         recent.at[ii, 'last name'] = name[-1]
#         if len(name) > 2:
#             recent.at[ii, 'middle name'] = ' '.join(name[1:-1])
#         else:
#             recent.at[ii, 'middle name'] = np.nan
# recent.to_csv('/home/innereye/Documents/recent_eng.csv', index=False)
# ## look for duplicates
# war = pd.read_csv('/home/innereye/Documents/oct7database - war.csv')
# data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
# namew = [war['שם פרטי'][x] + ' ' + war['שם משפחה'][x] for x in range(len(war))]
# named = np.array([data['שם פרטי'][x] + ' ' + data['שם משפחה'][x] for x in range(len(data))])
# dup = pd.DataFrame(columns=['pid','name'])
# for ii in range(len(namew)):
#     row = np.where(named == namew[ii])[0]
#     if len(row) > 1:
#         raise Exception(namew[ii])
#     elif len(row) == 1:
#         dup.loc[len(dup)] = [data['pid'].values[row][0], namew[ii]]
# dup.to_csv('/home/innereye/Documents/duplicates.csv', index=False)
#
# dup = pd.DataFrame(columns=['pid','name'])
# for ii in range(len(namew)):
#     row = np.where(named == named[ii])[0]
#     row = row[row != ii]
#     if len(row) == 1:
#         dup.loc[len(dup)] = [data['pid'].values[row][0], named[ii]]
# ## make sure hebrew names are okay
# ## add oct_7_9 not in oct7map
# # nopid = np.where([
# # for ii in
# ## break english
#
#
# ## add birth date
# ##
# #         btl_id = cref['btl_id'][icref]
# #         if btl_id > 0:
# #             ibtl = np.where(btl['Column 1'] == btl_id)[0]
# #             if len(ibtl) == 1:
# #                 ibtl = ibtl[0]
# #                 name = names['first'][icref]
# #             if ord(name[0]) > 1487:
# #                 df.at[ii, 'שם פרטי'] = name
# #                 df.at[ii, 'שם משפחה'] = names['last'][icref]
# #                 df.at[ii, 'שם נוסף'] = names['middle'][icref]
# #                 df.at[ii, 'כינוי'] = names['nick'][icref]
# #             else:
# #                 df.at[ii, 'first name'] = name
# #                 df.at[ii, 'last name'] = names['last'][icref]
# #                 df.at[ii, 'middle name'] = names['middle'][icref]
# #                 df.at[ii, 'nickname'] = names['nick'][icref]
# # df['status'] = map7['status']
# # df.to_excel('/home/innereye/Documents/database.xlsx', index=False)
# ## copy data to a new table
# # for ii in range(len(locs)):
# #     pid = cref['oct7map_pid'][ii]
# #     if pid > 0:
# #         row = np.where(map7['pid'] == pid)[0][0]
# #         locs.at[ii, 'oct7map_name'] = map7['name'][row]
# # locs['oct_7_9_loc'] = map['location']
# # for ii in range(len(locs)):
# #     pid = cref['oct7map_pid'][ii]
# #     if pid > 0:
# #         row = np.where(map7['pid'] == pid)[0][0]
# #         locs.at[ii, 'oct7map_loc'] = map7['location'][row]
# #         locs.at[ii, 'oct7map_subloc'] = map7['sublocation'][row]
# #         locs.at[ii, 'oct7map_est'] = map7['Estimated location?'][row]
# #         locs.at[ii, 'oct7map_coo'] = map7['geotag'][row]
# #         locs.at[ii, 'oct7map_source'] = map7['location_source'][row]
# # ## complete coordinates for missing geotag based on sublocation
# # # subloc = np.unique(locs['oct7map_subloc'][locs['oct7map_coo'].isnull()].values.astype(str))
# # subloc = {'232 Blocked Road': [31.399963, 34.474210],
# #           'Alumim Bomb Shelter (West)': [31.450412, 34.516401],
# #           "Be'eri Bomb Shelter": [31.428803, 34.496924],
# #           'Gama Junction Bomb Shelter (North)': [31.381336, 34.447480],
# #           'Gama Junction Bomb Shelter (West)': [31.380127, 34.447162],
# #           "Hostage Situation in Be'eri": [],
# #           'Main Stage': [31.397771, 34.469951],
# #           'Nahal Grar Bridge': [31.400212, 34.474301],
# #           'Nova Ambulance': [31.397351, 34.469556],
# #           'Nova Bar': [31.398900, 34.470031],
# #           'Nova Entrance Bomb Shelter': [31.400190, 34.473742],
# #           "Re'im Bomb Shelter (East)": [31.389740, 34.459447],
# #           "Re'im Bomb Shelter (West)": [31.3897815832395, 34.45805954741456],
# #           'Yellow Containers': [31.398628, 34.470782]}
# #
# # for ii in range(len(locs)):
# #     pid = cref['oct7map_pid'][ii]
# #     coo = str(locs['oct7map_coo'][ii])
# #     if pid > 0 and coo[:2] != '31':
# #         row = np.where(map7['pid'] == pid)[0][0]
# #         sl = map7['sublocation'][row]
# #         if str(sl) not in ['nan', 'None']:
# #             locs.at[ii, 'oct7map_coo'] = str(subloc[sl])[1: -1]
# #
# # ## complete missing data based on location
# # maploc = pd.read_csv('data/deaths_by_loc.csv')
# # locrow = np.where(~maploc['oct7map'].isnull())[0]
# # for lr in locrow:
# #     trow = np.where(locs['oct7map_loc'].values == maploc['oct7map'][lr])[0]
# #     for tr in trow:
# #         if str(locs['oct7map_coo'][tr])[:2] != '31':
# #             locs.at[tr, 'oct7map_coo'] = str(maploc['lat'][lr])+', '+str(maploc['long'][lr])
# #
# # ## sublocations not represented in oct_7_9
# # other = {'The pensioners bus in Sderot': '31.522808876615766, 34.59568825785523',
# #          'Sderot Police Station': '31.522808876615766, 34.59568825785523',
# #          'Erez': '31.55999246335105, 34.56505148304494',
# #          'Kerem Shalom': '31.228310751744882, 34.28445082924824',
# #          'COGAT Base': '31.55987823169991, 34.54622846569096'}
# #
# # for othr in list(other.keys()):
# #     trow = np.where(locs['oct7map_loc'].values == othr)[0]
# #     for tr in trow:
# #         if str(locs['oct7map_coo'][tr])[:2] != '31':
# #             locs.at[tr, 'oct7map_coo'] = other[othr]
# # ##
# # locs.to_csv('data/tmp_locs.csv', index=False)
# # ## compute distance
# # names = pd.read_csv('data/oct_7_9.csv')
# # names = group_locs(names)
# # # replace = [['בכניסה לעלומים'], ['ביה"ח שיפא'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
# # #            ['צומת בארי'], ['מיגונית בצומת רעים', 'צומת רעים'], ['סמוך לצומת רעים', 'צומת רעים'], ['חאן יונס'],['מיגונית חניון רעים', 'פסטיבל נובה'],
# # #            ['רצועת עזה', 'רצועת עזה, לא פורסם מיקום מדוייק'], ['דיר אל בלח'], ['מיגונית מפלסים','סמוך למפלסים']]  #
# # #
# # # for uu in replace:
# # #     names.loc[names['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into
# #
# # for ii in range(len(locs)):
# #     trow = np.where(maploc['name'].values == names['location'][ii])[0][0]
# #     coo79 = [maploc['lat'][trow], maploc['long'][trow]]
# #     try:
# #         coo7 = np.array(locs['oct7map_coo'][ii].replace(' ', '').split(',')).astype(float)
# #         dif = geodesic(coo7, coo79).km
# #         locs.at[ii, 'dif'] = np.round(dif, 1)
# #     except:
# #         locs.at[ii, 'dif'] = np.nan
# # locs.to_csv('data/tmp_locs.csv', index=False)
# #
# # ##
# # difs = locs.copy()
# # difs = difs[~difs['dif'].isnull()]
# # difs = difs.sort_values('dif', ascending=False, ignore_index=True)
# # difs = difs[difs['dif'] >= 1]
# # difs.to_csv('data/tmp_dif.csv', index=False)
# # ##
# # # locs = pd.read_csv('data/tmp_locs.csv')
# # # est = locs['oct7map_est'].values.astype(str)
# # # est = np.array([x.strip() for x in est])
# # # est[est == 'nan'] = 'None'
# # # est[est == ''] = 'None'
# # # estu = np.unique(est)
# # # dif = locs['dif'].values
# # # co = ['k*', '.c', '.b', '.g', '.k', '.r']
# # # plt.figure()
# # # for ig in range(len(estu)):
# # #     x = np.where(est == estu[ig])[0]
# # #     plt.plot(x, dif[x], co[ig], label=estu[ig])
# # # plt.legend()
# # # plt.xlabel('oct_7_9 row in table')
# # # plt.ylabel('difference in km')
# # # plt.grid()
# # # plt.title('distance by estimate type')
# #
# #
# #
# # # nameh = map7['hebrew_name'].values
# # # namee = map7['name'].values  # [(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
# # # map = pd.read_csv('data/oct_7_9.csv')
# # # name = map['eng'].values
# # # ##
# # # # missing = [x.strip() for x in namee if x.strip() not in name]
# # # missing = []
# # # for ii in range(len(name)):
# # #     row = np.where(namee == name[ii])[0]
# # #     if len(row) == 1:
# # #         map.at[ii, 'oct7map_pid'] = map7['pid'][row[0]]
# # #     else:
# # #         map.at[ii, 'oct7map_pid'] = 0
# # #         missing.append(ii)
# # # map['oct7map_pid'] = map['oct7map_pid'].values.astype(int)
# # # map.to_excel('/home/innereye/Documents/pid.xlsx', index=False)
# #
# # ##
