import pandas as pd
import os
import sys
import numpy as np
import re


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
    if '"' in db['שם פרטי'].values[0]:
        raise ValueError('Too many quotes in the file, please fix manually')
    converted = False
    if db['הספריה הלאומית'].str.contains('E+').any():
        print('converting scientific notation to string')
        correct = pd.read_excel('~/Documents/NLI.xlsx', 'manual', dtype={'nli_id': str})
        correct = correct[:np.where(correct['pid'] == 119)[0][0]+1]
        for ii in range(len(correct)):
            if str(db['הספריה הלאומית'][ii]) == 'nan':
                db.at[ii, 'הספריה הלאומית'] = ""
            else:
                nli_value = str(correct['nli_id'][ii])
                if nli_value != 'nan':
                    # Add quotes around the NLI ID
                    db.at[ii, 'הספריה הלאומית'] = f'"{nli_value}"'
                else:
                    db.at[ii, 'הספריה הלאומית'] = ""
        converted  = True
        # Save with quotes
    quoted = False
    if '"' not in db['הספריה הלאומית'].values[0]:
        print('adding quotes to NLI IDs')
        db['הספריה הלאומית'] = '"' + db['הספריה הלאומית'].astype(str) + '"'
        quoted = True
    if converted or quoted:
        db.to_csv('data/oct7database.csv', index=False)
        
        # Fix the triple quotes by reading as text and replacing
        with open('data/oct7database.csv', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace triple quotes with single quotes
        content = content.replace('"""', '"')
        content = content.replace('"nan"', '')
        
        with open('data/oct7database.csv', 'w', encoding='utf-8') as f:
            f.write(content)
     
        print('Fixed triple quotes in CSV file')
    



if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('use --db2map or --fix_nli, no other tools yet')
    elif args[1] == '--db2map':
        db2map(save=True, what='loc')
    elif args[1] == '--fix_nli':
        fix_nli()
    else:
        raise ValueError(f"unknown input argument {args[1]}")
