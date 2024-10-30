"""check cause of death (rockets etc)."""
import pandas as pd
# import Levenshtein
# import requests
import os
import numpy as np

local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True

# idf = pd.read_csv('data/deaths_idf.csv')
# idf_pid = idf['pid'].values
# front = pd.read_csv('data/front.csv')
map79 = pd.read_csv('data/oct_7_9.csv')
map_pid = map79['pid'].values
story = pd.read_csv('data/stories.csv')
story_pid = story['pid'].values
db = pd.read_csv('data/oct7database.csv')
if 'סיבת המוות' not in db.columns:
    db['סיבת המוות'] = np.nan
idx = np.where(db['סיבת המוות'].isnull())[0]
if len(idx) == 0:
    print('cause of death column is full')
else:
    for ii in idx:
        if db['pid'][ii] in map_pid:
            row = np.where(map_pid == db['pid'][ii])[0][0]
            if 'ירי רקטי' in map79['location'][row]:
                db.at[ii, 'סיבת המוות'] = 'רקטה; תלול מסלול'
                continue

        if db['pid'][ii] in story_pid:
            sty = ';'.join(story.values[ii,:].astype(str))
            if 'מיירט' in sty:
                db.at[ii, 'סיבת המוות'] = 'מיירט'
                continue
            elif 'כטב' in sty:
                db.at[ii, 'סיבת המוות'] = 'כטב"מ'
                continue
            elif 'רקט' in sty:
                if 'נ"ט' in sty:
                    db.at[ii, 'סיבת המוות'] = 'רקטה; כינון ישיר'
                    continue
                elif 'טרקטורים' in sty:
                    pass
                else:
                    db.at[ii, 'סיבת המוות'] = 'רקטה; תלול מסלול'
                    continue
            elif 'דריסה' in sty or 'נדרס' in sty:
                db.at[ii, 'סיבת המוות'] = 'דריסה'
                continue
            elif 'פיגוע' in sty:
                if 'פיגוע ירי' in sty or 'פיגוע הירי' in sty or 'יריות' in sty:
                    db.at[ii, 'סיבת המוות'] = 'פיגוע ירי'
                    continue
                elif 'פיגוע דקירה' in sty:
                    db.at[ii, 'סיבת המוות'] = 'פיגוע דקירה'
                    continue
                else:
                    db.at[ii, 'סיבת המוות'] = 'פיגוע'
                    continue
            elif 'ירי צלף' in sty:
                db.at[ii, 'סיבת המוות'] = 'צלף'
                continue
            elif 'פצמ' in sty:
                db.at[ii, 'סיבת המוות'] = 'פצמ"ר'
                continue
        if db['Role'][ii] == 'אזרח' and db['Event date'][ii] > '2023-10-07':
            db.at[ii, 'סיבת המוות'] = '???'


story['סיבת המוות'] = db['סיבת המוות']
story.to_csv('~/Documents/stories.csv', index=False)

