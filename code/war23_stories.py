'''
collect ynet and haaretz stories
'''
import pandas as pd
import Levenshtein
import requests
import os
import numpy as np
ynet = pd.read_csv('data/ynetlist.csv')
haa0 = pd.read_csv('data/deaths_haaretz.csv')[::-1]
haa0.reset_index(drop=True, inplace=True)
haa1 = pd.read_csv('data/deaths_haaretz+.csv')
haak = pd.read_csv('data/kidnapped_haaretz.csv')
db = pd.read_csv('data/oct7database.csv')
columns = ['pid', 'שם פרטי','שם נוסף' ,'כינוי' ,'שם משפחה']
# df = pd.DataFrame(columns=columns)
df = pd.read_csv('data/stories.csv')
if not all(df['pid'] == db['pid'][:len(df)]):
    ibad = np.where(df['pid'].values != db['pid'].values[:len(df)])[0][0]
    print(f"stories: {df['שם פרטי'][ibad]} {df ['שם משפחה'][ibad]} pid {int(df['pid'][ibad])}")
    raise Exception('PID are not the same for DB and Stories')
for col in columns:
    df[col] = db[col]

issues = [['משה אל','משהאל'], ['גולימה סמצאו', 'גולימה שמואל סמצאו'],['״טייגר״ האגוס ברהה','ברהה וולדרפאל האגוס']]
issues += [['דולב מלכה', 'דולב חיים מלכה'][::-1]]
for issue in issues:
    haa0['name'] = haa0['name'].str.replace(issue[0], issue[1])
shift_at = ['תמר טורפיאשוילי', "ג'יאנה ליו","עידו אפל",'אורי בר אור','אליה הלל','סהר סודאי', 'זהיגו ליו', 'אביהוא מורי', ' סאו יונגקאי', 'רן יעבץ',
            "ולרי צ'פונוב"]
shift = 0
for ii in np.where(~haa1['pid'].isnull())[0]:
    name1 = haa1['name'][ii]
    if name1 in shift_at:
        shift += 1
    else:
        parts = len(name1.split(' '))
        name0 = ' '.join(haa0['name'][ii-shift].split(' ')[-parts:])
        story0 = haa0['story'][ii-shift]
        found = True
        if name1 not in name0:
            dist = Levenshtein.distance(name1, name0)
            if dist > 2:
                row0 = np.where(haa0['name'].str.contains(name1))[0]
                if len(row0) == 1:
                    shift = ii - row0[0]
                    name0 = ' '.join(haa0['name'][ii-shift].split(' ')[-parts:])
                    story0 = haa0['story'][ii-shift]
                else:
                    print(f"stories.py failed for haaretz ii={ii} name0={name0} name1={name1}")
                    found = False
                    shift += 1
        if found:
            row = np.where(db['pid'].values == haa1['pid'][ii])[0][0]
            if name0 != df['haaretz name'][row]:
                print(f"changed haaretz name from {df['haaretz name'][row]} to {name0}")
                df.at[row, 'haaretz name'] = name0
            if len(str(story0)) > len(str(df['haaretz story'][row])):
                print(f"changed haaretz story from {df['haaretz story'][row]} to {story0}")
                df.at[row, 'haaretz story'] = story0
## kidnapped
for ii in np.where(db['Status'].str.contains('kidnapped'))[0]:
    row = np.where(haak['name'].str.contains(db['שם פרטי'][ii]) & haak['name'].str.contains(db['שם משפחה'][ii]))[0]
    if len(row) != 1:
        print('no kidnapped for '+str(ii))
    else:
        already = str(df['haaretz story'][ii]) + '; '
        already = already.replace('nan; ', '')
        df.at[ii, 'haaretz name'] = haak['name'][row[0]]
        kidnapped_story = kidnapped_story.replace('nan', '')
        df.at[ii, 'haaretz story'] = already + kidnapped_story
        
## ynet
for ii in np.where(~ynet['pid'].isnull())[0]:
    ynet_pid = ynet['pid'][ii]
    if ynet_pid not in [1371]:
        row = np.where(db['pid'].values == ynet_pid)[0][0]
        df.at[row, 'ynet name'] = f"{ynet['שם פרטי'][ii]} {ynet['שם משפחה'][ii]}"
        df.at[row, 'ynet story'] = ynet['מידע על המוות'][ii]
##
df.to_csv('~/Documents/stories.csv', index=False)

    
