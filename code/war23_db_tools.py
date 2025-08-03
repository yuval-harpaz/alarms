import pandas as pd
import os
import sys
import numpy as np
# import re


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
##


def db2map(save=True, what='loc'):
    """
    copy fields from oct7database.csv to oct_7_0.csv
    :param save: bool
        True for saving to oct_7_0.csv
    :param what: str
        'all', 'date', 'loc'
    :return: df
    """
    db = pd.read_csv('data/oct7database.csv')
    map = pd.read_csv('data/oct_7_9.csv')
    kidnapped = [915, 29, 568, 192, 193, 482, 626, 581, 1432]  # not kidnapped in oct7map
    pid = db['pid'].values
    ignore = [1420]
    changes = False
    if what in ['all', 'loc']:
        for ii in range(len(map)):
            if map['pid'][ii] in ignore:
                continue
            row = np.where(pid == map['pid'][ii])[0][0]
            stat = db['Status'][row]
            if 'idnap' in stat or 'aptiv' in stat or map['pid'][ii] in kidnapped:
                loc = db['מקום המוות'][row]
            else:
                loc = db['מקום האירוע'][row]
            if map['location'][ii] != loc:
                print([map['pid'][ii], map['fullName'][ii], stat, loc, map['location'][ii]])
                map.at[ii, 'location'] = loc
                changes = True
    if what in ['all', 'date']:
        raise Exception('no support for dates yet')
        for ii in range(len(map)):
            row = np.where(pid == map['pid'][ii])[0][0]
            stat = db['Status'][row]
            if 'idnap' in stat or 'aptiv' in stat or map['pid'][ii] in kidnapped:
                loc = db['מקום המוות'][row]
            else:
                loc = db['מקום האירוע'][row]
            if map['location'][ii] != loc:
                print([map['pid'][ii], map['fullName'][ii], stat, loc, map['location'][ii]])
                map.at[ii, 'location'] = loc
                changes = True
    if save and changes:
        map.to_csv('data/oct_7_9.csv', index=False)
        print('saved to oct_7_9')
    else:
        return map

def fix_nli():
    """
    fix the 'הספריה הלאומית' column in oct7database.csv
    :return: None
    """
    db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
    with open('data/oct7database.csv', 'r', encoding='utf-8') as f:
        content0 = f.read()
    if content0[0] == '"':
        db.to_csv('data/oct7database.csv', index=False)
        db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
        with open('data/oct7database.csv', 'r', encoding='utf-8') as f:
            content0 = f.read()

    first = content0.index('987012802875705171')
    isquote = False
    if content0[first-1] == '"':
        isquote = True
    
    if '"' in db['שם פרטי'].values[0]:
        raise ValueError('Too many quotes in the file, please fix manually')
    # converted = False
    # quoted = False
    if db['הספריה הלאומית'].str.lower().str.contains('e+').any():
        raise ValueError('There are E+ NLI, revert to previous version')
        # print('converting scientific notation to string')
        # correct = pd.read_excel('~/Documents/NLI.xlsx', 'manual', dtype={'nli_id': str})
        # correct = correct[:np.where(correct['pid'] == 119)[0][0]+1]
        # for ii in range(len(correct)):
        #     if str(db['הספריה הלאומית'][ii]) == 'nan':
        #         db.at[ii, 'הספריה הלאומית'] = ""
        #     else:
        #         nli_value = str(correct['nli_id'][ii])
        #         if nli_value != 'nan':
        #             # Add quotes around the NLI ID
        #             db.at[ii, 'הספריה הלאומית'] = f'"{nli_value}"'
        #         else:
        #             db.at[ii, 'הספריה הלאומית'] = ""
        # converted  = True
        # Save with quotes
    elif not isquote:
        db['הספריה הלאומית'] = '"' + db['הספריה הלאומית'].astype(str) + '"'
        db.to_csv('data/oct7database.csv', index=False)
    
        # Fix the triple quotes by reading as text and replacing
    with open('data/oct7database.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('"nan"', '')
        with open('data/oct7database.csv', 'w', encoding='utf-8') as f:
            f.write(content)
    if '"""' in content:
        while '"""' in content:
            # Replace triple quotes with single quotes
            content = content.replace('"""', '"')
        with open('data/oct7database.csv', 'w', encoding='utf-8') as f:
            f.write(content)
            print('Fixed triple quotes in CSV file')
    
def compare_nli(compare_to='~/Documents/NLI 4 oct7database - manual.csv'):
    """
    compare the NLI IDs in oct7database.csv and NLI 4 oct7database - manual.csv
    :param compare_to: str
        path to the NLI 4 oct7database - manual.csv file
    :return: list of PIDs that are only in db, only in update, and mismatched
    """
    uptodate = pd.read_csv(compare_to, dtype={'הספריה הלאומית': str})
    db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
    min_len = min([len(db), len(uptodate)])
    if np.mean(db['pid'].values[:min_len] == uptodate['pid'].values[:min_len]) != 1:
        first_unequal = np.where(db['pid'].values[:min_len] != uptodate['pid'].values[:min_len])[0][0]
        print('pid issues, first one for pid ' + str(db['pid'].values[first_unequal]) + ' at index ')
        raise ValueError('pid mismatch between oct7database.csv and NLI 4 oct7database - manual.csv')
    only_db = []
    only_update = []
    mismatch = []
    for ii in range(min([len(db), len(uptodate)])):
        if str(db['הספריה הלאומית'][ii]) != 'nan' and str(uptodate['הספריה הלאומית'].values[ii]) == 'nan':
            print(f"pid {db['pid'][ii]} has NLI ID only in db")
            only_db.append(db['pid'][ii])
        elif str(db['הספריה הלאומית'][ii]) == 'nan' and str(uptodate['הספריה הלאומית'].values[ii]) != 'nan':
            # print(f"pid {db['pid'][ii]} has NLI ID only in uptodate")
            only_update.append(db['pid'][ii])
        elif str(db['הספריה הלאומית'][ii]) != str(uptodate['הספריה הלאומית'].values[ii]):
            if 'e+' in str(db['הספריה הלאומית'][ii]).lower():
                only_update.append(db['pid'][ii])
            else:
                print(f"pid {db['pid'][ii]} has different NLI ID in db: {db['הספריה הלאומית'][ii]} vs {uptodate['הספריה הלאומית'].values[ii]}")
                mismatch.append(db['pid'][ii])
    return only_db, only_update, mismatch



def fill_nli():
    """
    fill nli from NLI 4 oct7database - manual.csv.
    first download from https://docs.google.com/spreadsheets/d/1-f2JeU3BjIuP8-wBPZm2mCR172HJQKCuNuGao4AnHKg/edit?gid=25742010#gid=25742010
    """
    uptodate = pd.read_csv('~/Documents/NLI 4 oct7database - manual.csv', dtype={'הספריה הלאומית': str})
    db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
    # check pid are the same
    # min_len = min([len(db), len(uptodate)])
    # if np.mean(db['pid'].values[:min_len] == uptodate['pid'].values[:min_len]) != 1:
    #     first_unequal = np.where(db['pid'].values[:min_len] != uptodate['pid'].values[:min_len])[0][0]
    #     print('pid issues, first one for pid ' + str(db['pid'].values[first_unequal]) + ' at index ')
    #     raise ValueError('pid mismatch between oct7database.csv and NLI 4 oct7database - manual.csv')
    # # check differences
    # only_db = []
    # only_update = []
    # mismatch = []
    # for ii in range(min([len(db), len(uptodate)])):
    #     if str(db['הספריה הלאומית'][ii]) != 'nan' and str(uptodate['הספריה הלאומית'].values[ii]) == 'nan':
    #         print(f"pid {db['pid'][ii]} has NLI ID only in db")
    #         only_db.append(db['pid'][ii])
    #     elif str(db['הספריה הלאומית'][ii]) == 'nan' and str(uptodate['הספריה הלאומית'].values[ii]) != 'nan':
    #         # print(f"pid {db['pid'][ii]} has NLI ID only in uptodate")
    #         only_update.append(db['pid'][ii])
    #     elif str(db['הספריה הלאומית'][ii]) != str(uptodate['הספריה הלאומית'].values[ii]):
    #         if 'e+' in str(db['הספריה הלאומית'][ii]).lower():
    #             only_update.append(db['pid'][ii])
    #         else:
    #             print(f"pid {db['pid'][ii]} has different NLI ID in db: {db['הספריה הלאומית'][ii]} vs {uptodate['הספריה הלאומית'].values[ii]}")
    #             mismatch.append(db['pid'][ii])
    only_db, only_update, mismatch = compare_nli()
    #alert issues
    if len(only_db) > 0:
        print('The following PIDs have NLI IDs only in oct7database.csv:')
        print(only_db)
    if len(mismatch) > 0:
        print('The following PIDs have different NLI IDs in oct7database.csv and NLI 4 oct7database - manual.csv:')
        print(mismatch)
    if len(only_update) > 0:
        print(f'There are {len(only_update)} to update')
    if len(only_db) > 0 and len(only_update) > 0:
        raise ValueError('Resolve issues before update')
    elif len(only_update) > 0:
        for jj, pid in enumerate(only_update):
            row = np.where(db['pid'].values == pid)[0][0]
            nli_value = uptodate['הספריה הלאומית'].values[row]
            if str(nli_value) == 'nan':
                raise ValueError(f"pid {pid} has nan NLI value in uptodate")
            else:
                db.at[row, 'הספריה הלאומית'] = f'"{nli_value}"'
        db.to_csv('data/oct7database.csv', index=False)
    else:
        print ('No updates needed, all NLI IDs are up to date')
        # fix_nli()


def eng_loc(heb_empties=True):
    """
    convert to English the location names in oct7database based on deaths_by_loc
    """
    db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
    loc = pd.read_csv('data/deaths_by_loc.csv')
    converter = pd.read_csv('~/Documents/sublocation_converter.csv')
    #dict from df
    conv = dict(zip(converter['sublocation db'], converter['sublocation']))
    def convert_columns(input_col='מקום האירוע', output_col='Event location'):
        for ii in range(len(db)):
            heb = str(db[input_col][ii])
            if heb != 'nan':
                if heb in loc['name'].values:
                    eng = loc['eng'][loc['name'] == heb].values[0]
                    db.at[ii, output_col] = eng
                elif heb in conv.keys():
                    eng = conv[heb]
                    db.at[ii, output_col] = eng
                elif heb_empties:
                    db.at[ii, output_col] = heb
    convert_columns()
    convert_columns(input_col='מקום המוות', output_col='Death location')
    db.to_csv('data/oct7database.csv', index=False)
    return db
    


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('use --db2map or --fix_nli, no other tools yet')
    elif args[1] == '--db2map':
        db2map(save=True, what='loc')
    elif args[1] == '--fix_nli':
        fix_nli()
        # raise DeprecationWarning('use --fill_nli instead')
    elif args[1] == '--fill_nli':
        fill_nli()
    else:
        raise ValueError(f"unknown input argument {args[1]}")
