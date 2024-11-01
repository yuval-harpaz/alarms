"""Look up missing event location in front table."""
import pandas as pd
import os
import numpy as np
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
idf = pd.read_csv('data/deaths_idf.csv')
front = pd.read_csv('data/front.csv')
db = pd.read_csv('data/oct7database.csv')
idfid = idf['pid'].values
missing = np.where(db['מקום האירוע'].isnull() &
                   np.array([id in idfid for id in db['pid']]))[0]
ignore_pid = [1297, 2045]  # did not die in front
ignore = [np.where(db['pid'] == x)[0][0] for x in ignore_pid]
missing = [x for x in missing if x not in ignore]


##
def complete_event_loc():
    """Look up missing event location in front table."""
    changed = False
    for ii in missing:
        row = np.where(idf['pid'].values == db['pid'][ii])[0][0]
        loc = str(front['front'][row])
        if loc not in ['nan', 'תאונה']:
            db.at[ii, 'מקום האירוע'] = loc
            print(f"fron {loc} was added as event loc for pid {db['pid'][ii]}")
            changed = True
    if changed:
        db.to_csv('data/oct7database.csv', index=False)


##
if __name__ == '__main__':
    complete_event_loc()
    # argv = sys.argv
    # if len(argv) > 1 and argv[1] == '-a':
    #     print('checking previous')
    #     goover()
