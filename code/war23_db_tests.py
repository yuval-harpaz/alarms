import pandas as pd
import os
import numpy as np
import unittest
import sys
sys.path.append('code')
from war23_db_tools import compare_nli, loc_match
from war23_idf2db import idf_mismatch
local = '/home/yuval/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
else:
    url = os.environ['oct7map']
try:
    map7 = pd.read_json(url)
except:
    print('no internet?')


# data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
data = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
# omi = pd.read_csv('/home/innereye/Documents/oct7database - omissions.csv')
kidn = pd.read_csv('data/kidnapped.csv')
idf = pd.read_csv('data/deaths_idf.csv')
adit = pd.read_csv('data/oct7database_additional.csv')
##
''' TODO
check that middle names and nicknames are present for both languages
check that all parts of a name are present in the corresponding url
'''


##
with open('data/oct7database.csv', 'r', encoding='utf-8') as f:
    db_txt = f.read()
class TestNLI(unittest.TestCase):
    def all_quotes(self):
        if db_txt[0] == '"':
            print('first pid starts with "')
        self.assertNotEqual(db_txt[0], '"')
    def quoted_nli(self):
        before_first_nli = db_txt[db_txt.index('9870128028757')-1]
        if before_first_nli != '"':
            print('first nli should start with "')
        self.assertEqual(before_first_nli, '"')

    def nli_update(self):
        only_db, only_update, mismatch = compare_nli()
        if len(only_db) > 0:
            print('The following PIDs have NLI IDs only in oct7database.csv:')
            print(only_db)
        self.assertEqual(len(only_db), 0)
        if len(only_update) > 0:
            print('The following PIDs have NLI IDs only in NLI 4 oct7database - manual.csv:')
            print(only_update)
        self.assertEqual(len(only_update), 0)
        if len(mismatch) > 0:
            print('The following PIDs have mismatched NLI IDs:')
            print(mismatch)
        self.assertEqual(len(mismatch), 0)



def duplicates(pid, names):
    dup = pd.DataFrame(columns=['idx', 'pid', 'name'])
    for ii in range(len(names)):
        row = np.where(names == names[ii])[0]
        row = row[row != ii]
        if len(row) == 1:
            dup.loc[len(dup)] = [ii, pid[row[0]], names[ii]]
        elif len(row) > 1:
            if names[ii] in ['עמית כהן', 'Amit Cohen']:
                dup.loc[len(dup)] = [ii, pid[row[0]], names[ii]]
                continue
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
    
    def duplicate_additionals(self):
        pid = np.array(list(data['pid']) + list(adit['pid']))
        dup_pid = duplicates(pid, pid)
        duplicates_length = len(dup_pid)
        if duplicates_length > 0:
            print(f'Additionals Duplicates!!!! {np.unique(dup_pid["pid"])}'.replace('[', '').replace(']', ''))
        self.assertEqual(duplicates_length, 0)
    
    def duplicate_heb(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            names.append(data['שם פרטי'][ii] + ' ' + data['שם משפחה'][ii])
        names = np.array(names)
        dup_heb = duplicates(pid, names)
        dup_names = np.unique(dup_heb['name'])
        okay_dup = np.sort(['אור מזרחי', 'דניאל כהן', 'עמית כהן', 'רותם לוי', 'לידור לוי', 'יקיר לוי', 'עמית לוי', 'נדב כהן', 'אברהם כהן', 'בן כהן'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('Hebrew Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_heb.to_csv('/home/yuval/Documents/dup.csv', index=False)
            print(' See: Documents/dup.csv')
        self.assertEqual(duplicates_length, len(okay_dup))

    def duplicate_eng(self):
        pid = data['pid'].values
        names = []
        for ii in range(len(data)):
            if data['first name'][ii] != '??':
                names.append(data['first name'][ii] + ' ' + data['last name'][ii])
        names = np.array(names)
        dup_eng = duplicates(pid, names)
        dup_names = np.unique(dup_eng['name'])
        okay_dup = np.sort(['Or Mizrahi', 'Daniel Cohen', 'Amit Cohen', 'Ohad Cohen',
                            'Nadav Cohen', 'Rotem Levi', 'Amit Levi', 'Avraham Cohen', 'Ben Cohen'])
        duplicates_length = len(dup_names)
        bad_name = [x for x in dup_names if x not in okay_dup]
        if duplicates_length != len(okay_dup):
            print('English Name duplicates!!!!'+str(bad_name).replace('[', '').replace(']', ''))
            dup_eng.to_csv('/home/yuval/Documents/dup_eng.csv', index=False)
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

    def rank_name(self):
        pid_rank = [data['pid'][x] for x in range(len(data)) if data['first name'][x] in ['sergeant', 'sergent', 'captain', 'lieutenant', 'major', 'colonel', 'class']]
        if len(pid_rank) > 0:
            print(f'rank in first name!!!! {pid_rank}'.replace('[', '').replace(']', ''))
        self.assertEqual(len(pid_rank), 0)
    
    def duplicate_nli(self):
        pid = data['pid'].values
        nli = data['הספריה הלאומית'].values
        dup_nli = duplicates(pid, nli)
        dupu = np.unique(dup_nli['name'])
        duplicates_length = len(dupu)
        if duplicates_length > 0:
            print(f'{duplicates_length} NLI Duplicates!!!! {dupu}')
        self.assertEqual(duplicates_length, 0)




map79 = pd.read_csv('data/oct_7_9.csv')
map79 = map79[map79['pid'] != 1420]  # zivz ovitz is in additionals
map79 = map79.reset_index(drop=True)
pid79 = map79['pid'].values
# for kidnapped death loc / date is given in oct 7 9 instead of event
as_kidnapped = [568, 581, 626, 915, 1432]
event_or_death = []
for ii in range(len(map79)):
    row = np.where(data['pid'].values == map79['pid'][ii])[0][0]
    eod = 'event'
    if 'idnapp' in data['Status'][row] or map79['pid'][ii] in as_kidnapped:
        eod = 'death'
    event_or_death.append(eod)
dayfirst = '.' in map79['date'][0]

class Test79(unittest.TestCase):
    def extras79(self):
        pid = data['pid'].values
        ext = [x for x in map79['pid'] if x not in pid]
        n_extra = len(ext)
        if n_extra > 0:
            print(f'OCT_7_9 PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def unique_pid79(self):
        len_unique = len(pid79) - len(np.unique(pid79))
        if len_unique > 0:
            dup79 = np.unique([x for x in pid79 if np.sum(pid79 == x) > 1])
            print(f'OCT_7_9 PID Not Unique!!!! {dup79}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)

    def loc79(self):
        pid = data['pid'].values
        n_issues = 0
        for ii in range(len(map79)):
            row = np.where(pid == map79['pid'][ii])[0][0]
            if event_or_death[ii] == 'death':
                loc = str(data['מקום המוות'][row])
            else:
                loc = str(data['מקום האירוע'][row])
            if not loc_match(loc, map79['location'][ii]):
                n_issues += 1
                print(f"OCT_7_9 location for {map79['eng'][ii]} ({map79['pid'][ii]}) is {map79['location'][ii]}, not {loc}")
        self.assertEqual(n_issues, 0)

    def date79(self):
        no_date = [19, 207, 556]
        wounded = [901, 1704, 1707, 1733]
        pid = data['pid'].values
        n_issues = 0
        for ii in range(len(map79)):
            row = np.where(pid == map79['pid'][ii])[0][0]
            if event_or_death[ii] == 'death':
                date = data['Death date'][row]
            else:
                date = data['Event date'][row]
            date = pd.to_datetime(date)
            date79 = pd.to_datetime(map79['date'][ii], dayfirst=dayfirst)
            if date != date79 and data['pid'][row] not in wounded and data['pid'][row] not in no_date:
                n_issues += 1
                print(f"OCT_7_9 date for {map79['eng'][ii]} ({map79['pid'][ii]}) is {map79['date'][ii]}, not {date}")
        self.assertEqual(n_issues, 0)

    def nova79(self):
        pid = data['pid'].values
        n_miss_db = 0
        n_miss_79 = 0
        total79 = 0
        totaldb = 0
        for ii in range(len(map79)):
            row = np.where(pid == map79['pid'][ii])[0][0]
            if 'נובה' in str(map79['comment'][ii]):
                total79 += 1
                if 'Nova' not in str(data['Party'][row]):
                    n_miss_db += 1
                    print('no nova in db Party for '+str(data['pid'][row]))
            if 'Nova' in str(data['Party'][row]):
                if 'killed' in data['Status'][row].lower():
                    totaldb += 1
                if 'נובה' not in str(map79['comment'][ii]):
                    n_miss_79 += 1
                    print('no nova in map_7_9 comment for '+str(data['pid'][row]))
        self.assertEqual(n_miss_db, 0)
        self.assertEqual(n_miss_db, 0)
        self.assertEqual(total79, totaldb)



haa = pd.read_csv('data/deaths_haaretz+.csv')
class TestHaa(unittest.TestCase):
    def extras_haa(self):
        pid = data['pid'].values
        ext = [x for x in haa['pid'] if x not in pid]
        ext = np.array(ext)
        ext = np.unique(ext[~np.isnan(ext)]).astype(int)
        ext = [x for x in ext if x not in adit['pid'].values]  # not in DB but in additionals
        n_extra = len(ext)
        if n_extra > 0:
            print(f'haaretz+ PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def extras_kidnapped(self):
        pid = data['pid'].values
        pid_kidn = kidn['pid'].values
        extras = [x for x in pid_kidn if x not in pid]
        n_extra = len(extras)
        if n_extra > 0:
            print(f'kidnapped PID Not in DB!!!! {extras}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)
    def missing_haa(self):  # TODO: add kidnapped
        pid = data['pid'].values
        pid_kidn = kidn['pid'].values
        pid_haa = haa['pid'].values
        missing = [x for x in pid if x not in pid_haa]
        missing = np.array(missing)
        missing = np.unique(missing[~np.isnan(missing)]).astype(int)
        missing = [x for x in missing if x not in pid_kidn]
        missing = [x for x in missing if x not in range(2024, 2031)]  # Gazans
        n_extra = len(missing)
        if n_extra > 0:
            print(f'pid not in haaretz+!!!! {missing}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)
    def unique_haa(self):
        pid_haa = haa['pid'].values
        pid_haa = pid_haa[~np.isnan(pid_haa)]
        len_unique = len(pid_haa) - len(np.unique(pid_haa))
        if len_unique > 0:
            dup_haa = np.unique([x for x in pid_haa if np.sum(pid_haa == x) > 1])
            print(f'haartz+ PID Not Unique!!!! {dup_haa}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)
idf_bad_name = idf_mismatch()
# idf_bad_name = [2115, 1725, 2017, 2143, 2619, 2689]
#
class TestIDF(unittest.TestCase):
    def unique_idf(self):
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)]
        len_unique = len(pid_idf) - len(np.unique(pid_idf))
        if len_unique > 0:
            dup_idf = np.unique([x for x in pid_idf if np.sum(pid_idf == x) > 1])
            print(f'idf PID Not Unique!!!! {dup_idf}'.replace('[', '').replace(']', ''))
        self.assertEqual(len_unique, 0)
    def extras_idf(self):
        pid = data['pid'].values
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)].astype(int)
        ext = [x for x in pid_idf if x not in pid]
        ext = np.array(ext)
        # ext = np.unique(ext[~np.isnan(ext)]).astype(int)
        n_extra = len(ext)
        if n_extra > 0:
            print(f'idf PID Not in DB!!!! {ext}'.replace('[', '').replace(']', ''))
        self.assertEqual(n_extra, 0)

    def name_idf(self):
        pid = data['pid'].values
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)].astype(int)
        mismatch = 0
        pid_mismatch = []
        for ii in range(len(pid_idf)):
            if pid_idf[ii] in idf_bad_name:
                continue
            row = np.where(pid == pid_idf[ii])[0]
            if len(row) == 1:
                row = row[0]
                first = data['שם פרטי'][row]
                name = idf['name'][ii]
                if first not in name:
                    print(' ii ' + str(ii))
                    print(f'IDF: pid={idf["pid"][ii]}, {first} not in {name}')
                    mismatch += 1
                    pid_mismatch.append(idf["pid"][ii])
        if mismatch > 0:
            print(f"idf name doesn't match !!!! {pid_mismatch}".replace('[', '').replace(']', ''))
        self.assertEqual(mismatch, 0)

    def lastname_idf(self):
        pid = data['pid'].values
        pid_idf = idf['pid'].values
        pid_idf = pid_idf[~np.isnan(pid_idf)].astype(int)
        mismatch = 0
        pid_mismatch = []
        known = [1643, 1266, 287]
        for ii in range(len(pid_idf)):
            if pid_idf[ii] in idf_bad_name:
                continue
            row = np.where(pid == pid_idf[ii])[0]
            if len(row) == 1:
                row = row[0]
                last = data['שם משפחה'][row]
                last = last.replace('רזיאל רוזנברג', 'רזיאל')
                name = idf['name'][ii].replace('(', '').replace(')', '')
                if last not in name and idf["pid"][ii] not in known:
                    print(f'IDF: pid={idf["pid"][ii]}, {last} not in {name}')
                    mismatch += 1
                    pid_mismatch.append(idf["pid"][ii])
        if mismatch > 0:
            print(f"idf name doesn't match !!!! {pid_mismatch}".replace('[', '').replace(']', ''))
        self.assertEqual(mismatch, 0)


# class Location(unittest.TestCase):
#     def map7updated(self):
#         # db = pd.read_csv('data/oct7database.csv')
#         # map = pd.read_csv('data/oct_7_9.csv')
#         kidnapped = [915, 29, 568, 626, 139, 581, 1432, 135]  # not kidnapped in oct7map, event and death not in same location
#         pid = data['pid'].values
#         check = []
#         for ii in range(len(map79)):
#             row = np.where(pid == map79['pid'][ii])[0][0]
#             stat = str(data['Status (oct7map)'][row])
#             if 'idnap' in stat or 'aptiv' in stat or map79['pid'][ii] in kidnapped:
#                 loc = data['מקום המוות'][row]
#             else:
#                 loc = data['מקום האירוע'][row]
#             if map79['location'][ii] != loc:
#                 check.append([map79['pid'][ii], map79['fullName'][ii], stat, loc, map79['location'][ii]])
#         different_locations = len(check)
#         if different_locations > 0:
#             df = pd.DataFrame(check, columns=['pid', 'name', 'status', 'db', 'map'])
#             print(df)
#         self.assertEqual(different_locations, 0)
#         # df.to_csv('/home/innereye/Documents/check.csv', index=False)

##
rel = pd.read_csv('data/victims_relationship.csv')
pid_rel = rel['pid'].values


class Relations(unittest.TestCase):
    def mutual_partners(self):
        mut = rel['partners'].values
        bads = []
        for kk in np.where(~np.isnan(mut))[0]:
            row = np.where(rel['pid'].values == mut[kk])[0][0]
            if mut[row] != pid_rel[kk]:
                print(f'relations bad partner: expected {pid_rel[row]} to be a partner of {pid_rel[kk]}')
                bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)

    def mutual_siblings(self):
        mut = rel['siblings'].values
        bads = []
        for kk in range(len(mut)):
            if type(mut[kk]) == str:
                others = [int(x) for x in mut[kk].split(';')]
                for isib in range(len(others)):
                    row = np.where(rel['pid'].values == others[isib])[0][0]
                    if str(pid_rel[kk]) not in str(mut[row]):
                        print(f'relations bad siblings: expected {pid_rel[row]} to be a sibling of {pid_rel[kk]}')
                        bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)


    def mutual_parents(self):
        mut0 = rel['parents to'].values
        mut1 = rel['children of'].values
        bads = []
        for kk in range(len(mut0)):
            if type(mut0[kk]) == str:
                others = [int(x) for x in mut0[kk].split(';')]  # kids
                for iother in range(len(others)):
                    row = np.where(rel['pid'].values == others[iother])[0][0]
                    if str(pid_rel[kk]) not in str(mut1[row]):
                        print(f'relations bad parents: expected {pid_rel[row]} to be a child of {pid_rel[kk]}')
                        bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)

    def mutual_children(self):
        mut1 = rel['parents to'].values
        mut0 = rel['children of'].values
        bads = []
        for kk in range(len(mut0)):
            if type(mut0[kk]) == str:
                others = [int(x) for x in mut0[kk].split(';')]  # parents
                for iother in range(len(others)):
                    row = np.where(rel['pid'].values == others[iother])[0][0]
                    if str(pid_rel[kk]) not in str(mut1[row]):
                        print(f'relations bad children: expected {pid_rel[row]} to be a parent of {pid_rel[kk]}')
                        bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)

    def mutual_gparents(self):
        mut0 = rel['grdparents'].values
        mut1 = rel['grdchildren'].values
        bads = []
        for kk in range(len(mut0)):
            if type(mut0[kk]) == str:
                others = [int(x) for x in mut0[kk].split(';')]  # kids
                for iother in range(len(others)):
                    row = np.where(rel['pid'].values == others[iother])[0][0]
                    if str(pid_rel[kk]) not in str(mut1[row]):
                        print(f'relations bad grand parents: expected {pid_rel[row]} to be a grandchild of {pid_rel[kk]}')
                        bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)

    def mutual_gchildren(self):
        mut1 = rel['grdparents'].values
        mut0 = rel['grdchildren'].values
        bads = []
        for kk in range(len(mut0)):
            if type(mut0[kk]) == str:
                others = [int(x) for x in mut0[kk].split(';')]  # parents
                for iother in range(len(others)):
                    row = np.where(rel['pid'].values == others[iother])[0][0]
                    if str(pid_rel[kk]) not in str(mut1[row]):
                        print(f'relations bad grand children: expected {pid_rel[row]} to be a grandparent of {pid_rel[kk]}')
                        bads.append(kk)
        n_bads = len(bads)
        self.assertEqual(n_bads, 0)

    def no_row(self):
        pid = []
        all_pids = rel.values[:,7:14]
        all_pids = all_pids.flatten()
        for cell in all_pids:
            if str(cell) != 'nan':
                if type(cell) == float:
                    pid.append(str(int(cell)))
                else:
                    pid.extend(cell.split(';'))
        pid = np.unique(pid).astype('int64')
        extras = [x for x in pid if x not in pid_rel]
        if len(extras) > 0:
            print(f"extra PID as relative with no row of its own {extras}")
        self.assertEqual(extras, [])



def collect_issues(pid_a, pid_b):
    issues = []
    for ida in pid_a:
        if ida not in pid_b:
            issues.append(ida)
    for idb in pid_b:
        if idb not in pid_a:
            issues.append(idb)
    names = ''
    if len(issues) > 0:
        for pid in issues:
            nm = data['שם פרטי'][data['pid'] == pid].values[0] + ' '+ \
                 data['שם משפחה'][data['pid'] == pid].values[0]
            names += nm + '; '
        names = names[:-2]
    return issues, names


class TestKidnapped(unittest.TestCase):
    def alive(self):
        pid_kid = kidn['pid'].values[kidn['condition'] == "חטוף"]
        pid_db = data['pid'].values[data['Status'] == "kidnapped"]
        issues, names = collect_issues(pid_kid, pid_db)
        if len(names) > 0:
            print(f"kidnapped alive mismatch: {issues} {names}")
        self.assertEqual(names, '')
    def returned(self):
        pid_kid = kidn['pid'].values[kidn['condition'] == "הוחזר"]
        pid_db = data['pid'].values[data['Status'].str.contains('returned') | data['Status'].str.contains('retrieved')]
        issues, names = collect_issues(pid_kid, pid_db)
        if len(names) > 0:
            print(f"kidnapped returned mismatch: {issues} {names}")
        self.assertEqual(names, '')

##
# comparing the website (wix) with oct7database.csv as saved on github, see war23_api.py.
# getColumns is only asked for the pid column, the data itself is collected pid by pid with getRecords,
# which is the only way to get all the fields.
max_print = 10
wix_fields = ['link-oct7database-pid', 'memorialSiteTypeEn', 'memorialSiteTypeHe']  # made by wix, not uploaded
csv_only_columns = ['Event location class', 'Death location class']  # not in db2api, never uploaded
website = {}  # cache, filled by load_website


def load_website():
    """the data on the website, and the records as they should be according to oct7database.csv on github"""
    if 'site' in website.keys():
        return
    from war23_api import db as gitdb, pid2record, get_all_records
    records, not_found = get_all_records()
    site = {rec['pid']: rec for rec in records}
    expected = {}
    failed = []
    for pid in gitdb['pid'].values:
        try:
            expected[int(pid)] = pid2record(int(pid))
        except Exception as exc:
            failed.append([int(pid), str(exc)])
    site_fields = sorted(set([f for rec in site.values() for f in rec.keys()]))
    csv_fields = sorted(set([f for rec in expected.values() for f in rec.keys()]))
    website['site'] = site
    website['expected'] = expected
    website['failed'] = failed
    website['not_found'] = not_found
    website['fields'] = [f for f in csv_fields if f in site_fields and f != 'pid']
    website['not_on_site'] = [f for f in csv_fields if f not in site_fields]
    website['not_in_csv'] = [f for f in site_fields if f not in csv_fields]


def website2csv():
    """rebuild oct7database.csv from the website. returns the table and the columns which can not be filled"""
    load_website()
    from war23_api import db as gitdb, db2api
    columns = [c for c in gitdb.columns if c == 'pid' or
               (c in db2api.keys() and db2api[c] in website['fields'])]
    cant_rebuild = [c for c in gitdb.columns if c not in columns]
    rows = []
    for pid in sorted(website['site'].keys()):
        row = {'pid': pid}
        for col in columns[1:]:
            value = website['site'][pid].get(db2api[col])
            if type(value) == list:
                value = '; '.join([str(x) for x in value])
            elif col == 'הספריה הלאומית' and type(value) == str:
                value = value.split('/')[-1]  # pid2record turns the NLI id into a url
            row[col] = value
        rows.append(row)
    return pd.DataFrame(rows, columns=columns), cant_rebuild


def csv2website():
    """the records as they should be on the website, built from the csv on github with dictionaries.json"""
    load_website()
    return website['expected']


def report_mismatch(title, mismatch, left='website', right='github'):
    from war23_api import show
    print(f'{title}: {len(mismatch)} records differ!!!!')
    for pid, right_value, left_value in mismatch[:max_print]:
        print(f'   pid {pid}: {left} has {show(left_value)}, {right} has {show(right_value)}')
    if len(mismatch) > max_print:
        print(f'   ... and {len(mismatch) - max_print} more')


class TestWebsite(unittest.TestCase):
    def website_records(self):
        load_website()
        failed = website['failed']
        if len(failed) > 0:
            print(f'could not build a record for {[x[0] for x in failed]}'.replace('[', '').replace(']', ''))
            print(failed[0][1])
        if len(website['not_found']) > 0:
            print(f"getRecords did not return {website['not_found']}".replace('[', '').replace(']', ''))
        self.assertEqual(len(failed) + len(website['not_found']), 0)

    def website_fields(self):
        load_website()
        not_on_site = website['not_on_site']
        not_in_csv = [f for f in website['not_in_csv'] if f not in wix_fields]
        if len(not_in_csv) > 0:
            print('fields on the website which the csv knows nothing about!!!! ' +
                  str(not_in_csv).replace("'", '').replace('[', '').replace(']', ''))
        if len(not_on_site) > 0:
            print('fields the csv makes but no record on the website has!!!! ' +
                  str(not_on_site).replace("'", '').replace('[', '').replace(']', ''))
        self.assertEqual(len(not_on_site) + len(not_in_csv), 0)

    def website_missing(self):
        load_website()
        missing = [x for x in website['expected'].keys() if x not in website['site'].keys()]
        if len(missing) > 0:
            print(f'PID on github but not on the website!!!! {missing}'.replace('[', '').replace(']', ''))
        self.assertEqual(len(missing), 0)

    def website_extra(self):
        load_website()
        extra = [x for x in website['site'].keys() if x not in website['expected'].keys()]
        if len(extra) > 0:
            print(f'PID on the website but not on github!!!! {extra}'.replace('[', '').replace(']', ''))
        self.assertEqual(len(extra), 0)

    def csv_from_website(self):
        """website -> csv"""
        from war23_api import db as gitdb, same_value
        rebuilt, cant_rebuild = website2csv()
        unexpected = [c for c in cant_rebuild if c not in csv_only_columns]
        if len(unexpected) > 0:
            print('columns which can not be rebuilt from the website!!!! ' +
                  str(unexpected).replace("'", '').replace('[', '').replace(']', ''))
        row_of = {pid: row for row, pid in enumerate(gitdb['pid'].values)}
        n_issues = 0
        for col in rebuilt.columns[1:]:
            mismatch = []
            for ii in range(len(rebuilt)):
                pid = rebuilt['pid'][ii]
                if pid not in row_of.keys():  # reported by website_extra
                    continue
                csv_value = gitdb.at[row_of[pid], col]
                if not same_value(csv_value, rebuilt[col][ii], date='date' in col.lower()):
                    mismatch.append([pid, csv_value, rebuilt[col][ii]])
            n_issues += len(mismatch)
            if len(mismatch) > 0:
                report_mismatch(col, mismatch)
        self.assertEqual(n_issues, 0)

    def website_from_csv(self):
        """csv -> website"""
        from war23_api import same_value
        expected = csv2website()
        n_issues = 0
        for field in website['fields']:
            mismatch = []
            for pid, record in expected.items():
                if pid not in website['site'].keys():  # reported by website_missing
                    continue
                exp = record.get(field)
                got = website['site'][pid].get(field)
                if not same_value(exp, got, date=field.endswith('Date')):
                    mismatch.append([pid, exp, got])
            n_issues += len(mismatch)
            if len(mismatch) > 0:
                report_mismatch(field, mismatch)
        self.assertEqual(n_issues, 0)


##
if __name__ == '__main__':
    args = sys.argv
    oct7db_results = unittest.TestResult()
    if len(args) == 1:
        oct7suite = unittest.TestSuite(tests=[TestDuplicates('duplicate_pid'),
                                              TestDuplicates('duplicate_heb'),
                                              TestDuplicates('duplicate_eng'),
                                              TestDuplicates('duplicate_url'),
                                              TestDuplicates('rank_name'),
                                              TestDuplicates('duplicate_additionals'),
                                              TestDuplicates('duplicate_nli'),
                                              Test79('extras79'),
                                              Test79('unique_pid79'),
                                              Test79('loc79'),
                                              Test79('date79'),
                                              Test79('nova79'),
                                              TestHaa('extras_haa'),
                                              TestHaa('unique_haa'),
                                              TestIDF('unique_idf'),
                                              TestIDF('extras_idf'),
                                              TestIDF('name_idf'),
                                              TestIDF('lastname_idf'),
                                              TestKidnapped('alive'),
                                              TestKidnapped('returned'),
                                              TestNLI('all_quotes'),
                                              TestNLI('quoted_nli'),
                                              ]
                                       )
    elif args[1][0] == 'r':
        oct7db_results = unittest.TestResult()
        oct7suite = unittest.TestSuite(tests=[Relations('mutual_partners'),
                                              Relations('mutual_parents'),
                                              Relations('mutual_children'),
                                              Relations('mutual_gparents'),
                                              Relations('mutual_gchildren'),
                                              Relations('no_row'),
                                              Relations('mutual_siblings')])
    elif args[1][0] in ['a', 'w']:  # api / website
        oct7suite = unittest.TestSuite(tests=[TestWebsite('website_records'),
                                              TestWebsite('website_fields'),
                                              TestWebsite('website_missing'),
                                              TestWebsite('website_extra'),
                                              TestWebsite('csv_from_website'),
                                              TestWebsite('website_from_csv')])
    else:
        raise Exception('unrecognized options')
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
