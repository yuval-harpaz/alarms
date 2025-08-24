import sys
import pandas as pd
import os
import numpy as np
import re
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
## load data and run sanity checks
# only_new = False
# if only_new:
idf = pd.read_csv('data/deaths_idf.csv')
add = pd.read_csv('data/oct7database_additional.csv')
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
inew = np.where([x not in db['הנצחה'].values for x in idf['webpage'].values])[0]


def sane():
    """Sanity test."""
    missing = np.sum(idf['webpage'].isnull())
    if missing:
        raise Exception(f'{missing} idf missing webpage')
    wpu = np.unique(idf['webpage'])
    if len(wpu) < len(idf):
        raise Exception('idf webpage not usinque')

    debug = False
    div_last = [283, 401, 1266, 1643, 2399, 287, 1725, 2017, 2143]
    div_first = [2115]
    # idf_bad_name = [2115, 1725, 2017, 2143]
    for ii in np.where([x in idf['pid'].values for x in db['pid'].values])[0]:
        row = np.where(idf['pid'].values == db['pid'][ii])[0][0]
        if db['הנצחה'][ii] != idf['webpage'][row]:
            if debug:
                # db.at[ii, 'הנצחה'] = idf['webpage'][row]
                print('different webpages for pid ' + str(db['pid'][ii]))
            else:
                raise Exception('different webpages for pid ' + str(db['pid'][ii]))
        if (db['שם פרטי'][ii] not in idf['name'][row]) and (db['pid'][ii] not in div_first):
            if debug:
                # db.at[ii, 'הנצחה'] = idf['webpage'][row]
                print('different first name for pid ' + str(db['pid'][ii]))
            else:
                raise Exception('different first name for pid ' + str(db['pid'][ii]))
        if (db['שם משפחה'][ii] not in idf['name'][row]) and (db['pid'][ii] not in div_last):
            if debug:
                # db.at[ii, 'הנצחה'] = idf['webpage'][row]
                print('different last name for pid ' + str(db['pid'][ii]))
            else:
                raise Exception('different last name for pid ' + str(db['pid'][ii]))

##
def add_new():
    """Add new soldiers to DB."""
    if len(inew):
        for ii in inew:
            url = idf['webpage'][ii]
            if url in db['הנצחה'].values:
                raise Exception(f'url already in db : {url}')
        # db = pd.read_csv('data/oct7database.csv')
        ranks = ['sergeant', 'sergent', 'captain', 'lieutenant', 'major', 'colonel',
                 'chief warrant officer', 'warrant officer', 'corporal']
        for ii in inew:
            nameheb = idf['name'][ii].split(' ')
            already = np.where((db['שם פרטי'] == nameheb[0]) & (db['שם משפחה'] == nameheb[-1]))[0]
            if len(already) == 1:
                idb = already[0]
                pid = db['pid'][idb]
                print(idf['name'][ii] + ' same as ' + db['שם פרטי'][idb] + ' ' + db['שם משפחה'][idb]+'?')
                resp = input('confirm: y/!y')
                if resp != 'y':
                    raise Exception('complete DB from IDF manually')
            else:
                idb = len(db)
                pid = np.max(list(db['pid'])+list(add['pid'])) + 1
                db.at[idb, 'pid'] = pid
            db.at[idb, 'Status'] = 'killed'
            db.at[idb, 'Country'] = 'ישראל'
            db.at[idb, 'Gender'] = idf['gender'][ii]
            db.at[idb, 'הנצחה'] = idf['webpage'][ii]
            db.at[idb, 'שם פרטי'] = nameheb[0]
            db.at[idb, 'שם משפחה'] = nameheb[-1]
            db.at[idb, 'Residence'] = idf['from'][ii]
            db.at[idb, 'Age'] = idf['age'][ii]
            if len(nameheb) > 2:
                db.at[idb, 'שם נוסף'] = ' '.join(nameheb[1:-1])
            story = idf['story'][ii]
            if 'פצע' in story or 'נפטר' in story:
                same_day = False
            else:
                same_day = True
            db.at[idb, 'Death date'] = idf['death_date'][ii]
            if same_day:
                db.at[idb, 'Event date'] = idf['death_date'][ii]
            if 'כוננות' in story and 'כיתת' in story:
                db.at[idb, 'Role'] = 'כיתת כוננות'
            else:
                db.at[idb, 'Role'] = 'חייל'
            if 'רצוע' in story:
                if re.search(r'מרכז.רצוע', story, re.UNICODE):
                    db.at[idb, 'מקום האירוע'] = 'מרכז רצועת עזה'
                elif re.search(r'דרום.רצוע', story, re.UNICODE):
                    db.at[idb, 'מקום האירוע'] = 'דרום רצועת עזה'
                elif re.search(r'צפון.רצוע', story, re.UNICODE):
                    db.at[idb, 'מקום האירוע'] = 'צפון רצועת עזה'
                elif 'דרום לבנון' in story:
                    db.at[idb, 'מקום האירוע'] = 'דרום לבנון'
                # db.at[idb, 'Event location class (oct7map)'] = 'idf'
                # db.at[idb, 'Event location (oct7map)'] = db['מקום האירוע'][idb]
                if same_day:
                    db.at[idb, 'מקום המוות'] = db['מקום האירוע'][idb]
            en = idf['eng'][ii]
            name = ''
            if type(en) == str:
                if '(res.)' in en:
                    name = en[en.index('(res.)') + 6:].strip()
                elif 'class' in en.lower():
                    name = en[en.lower().index('class') + 5:].strip()
                else:
                    rank = [x for x in ranks if x in en.lower()]
                    if len(rank) > 0:
                        name = en[en.lower().index(rank[0]) + len(rank[0]):].strip()
                    else:
                        print(en)
            if len(name) > 0:
                name = name.split(' ')
                db.at[idb, 'first name'] = name[0]
                db.at[idb, 'last name'] = name[-1]
                if len(name) > 2:
                    db.at[idb, 'middle name'] = ' '.join(name[1:-1])
            idf.at[ii, 'pid'] = pid
        db.to_csv('data/oct7database.csv', index=False)
        idf.to_csv('data/deaths_idf.csv', index=False)


##
def haa():
    """Match Haaretz cases."""
    haa = pd.read_csv('data/deaths_haaretz+.csv')
    ismiss = np.where(haa['pid'].isnull() & (haa['status'] == 'חייל'))[0]
    if len(ismiss):
        for imiss in ismiss:
            name = haa['name'][imiss]
            search = True
            row = len(db)
            while search:
                if row == 0:
                    search = False
                else:
                    row -= 1
                # for row in np.arange(len(db)-1, -1, -1):
                    if db['שם פרטי'][row] in name and db['שם משפחה'][row] in name:
                        pid = db['pid'][row]
                        if pid not in haa['pid'].values:
                            haa.at[imiss, 'pid'] = pid
                            print(imiss)
                            search = False
    haa.to_csv('data/deaths_haaretz+.csv', index=False)


##
def goover():
    """Go over all soldiers and look for mismatch, fix from idf to db"""
    fields = [['Gender', 'gender'],
              ['webpage', 'הנצחה'][::-1],
              ['Residence', 'from'],
              ['Age', 'age']]
    changed = False
    for ii in np.where([x in idf['pid'].values for x in db['pid'].values])[0]:
        row = np.where(idf['pid'].values == db['pid'][ii])[0][0]
        for ifield in range(len(fields)):
            if ifield == 3:
                a = int(db[fields[ifield][0]][ii])
                b = int(idf[fields[ifield][1]][row])
            else:
                a = str(db[fields[ifield][0]][ii])
                b = str(idf[fields[ifield][1]][row]).replace('קיבוץ ', '').replace('קריית', 'קרית')
            if a != b:
                print(f"different {fields[ifield][0]} for pid {db['pid'][ii]}"+
                      f" {a} >> {b}")
                if a == 'nan':
                    db.at[ii, fields[ifield][0]] = b
                    changed = True
    if changed:
        db.to_csv('data/oct7database.csv', index=False)



##
if __name__ == '__main__':
    sane()
    add_new()
    haa()
    argv = sys.argv
    if len(argv) > 1 and argv[1] == '-a':
        print('checking previous')
        goover()
