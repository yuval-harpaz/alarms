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
    changes = False
    if what in ['all', 'loc']:
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


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('use --db2map, no other tools yet')
    elif args[1] == '--db2map':
        db2map(save=True, what='loc')
    else:
        raise ValueError(f"unknown input argument {args[1]}")
