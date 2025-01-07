"""collect ynet and haaretz stories."""
import pandas as pd
import Levenshtein
# import requests
import os
import numpy as np

local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
ynet = pd.read_csv('data/ynetlist.csv')
haa0 = pd.read_csv('data/deaths_haaretz.csv')[::-1]
haa0.reset_index(drop=True, inplace=True)
haa1 = pd.read_csv('data/deaths_haaretz+.csv')
haak = pd.read_csv('data/kidnapped_haaretz.csv')
db = pd.read_csv('data/oct7database.csv')
columns = ['pid', 'שם פרטי' ,'שם נוסף' ,'כינוי' ,'שם משפחה']
# df = pd.DataFrame(columns=columns)
df = pd.read_csv('data/stories.csv')
if not all(df['pid'] == db['pid'][:len(df)]):
    raise Exception('PID are not the same for DB and Stories')
for col in columns:
    for ii in range(len(db)):
        df.at[ii, col] = db[col][ii]

issues = [['משה אל','משהאל'], ['גולימה סמצאו', 'גולימה שמואל סמצאו'],['״טייגר״ האגוס ברהה','ברהה וולדרפאל האגוס']]
issues += [['דולב מלכה', 'דולב חיים מלכה'][::-1]]
for issue in issues:
    haa0['name'] = haa0['name'].str.replace(issue[0], issue[1])
shift_at = ['תמר טורפיאשוילי', "ג'יאנה ליו", 'זהיגו ליו', 'אביהוא מורי', ' סאו יונגקאי', 'רן יעבץ',
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
        if name1 not in name0:
            dist = Levenshtein.distance(name1, name0)
            if dist > 2:
                row = np.where(haa0['name'].str.contains(name1))[0]
                if len(row) == 1:
                    shift = ii - row[0]
                    name0 = ' '.join(haa0['name'][ii-shift].split(' ')[-parts:])
                    story0 = haa0['story'][ii-shift]
                else:
                    print(f"stories haaretz: cannot find {name1}")
                    shift += 1
                    continue
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
        kidnapped_story = str(haak['story'][row[0]])
        # kidnapped_story = kidnapped_story.replace('nan', '')
        if kidnapped_story != 'nan' and kidnapped_story not in already:
            df.at[ii, 'haaretz story'] = already.split('; ')[0] + '; ' + kidnapped_story
            print(f"added kidnapped story for {haak['name'][row[0]]} {kidnapped_story}")

## ynet
skip = [1371]  # pid in ynet but not in DB (maybe additional)
for ii in np.where(~ynet['pid'].isnull())[0]:
    row = np.where(db['pid'].values == ynet['pid'][ii])[0]
    if len(row) == 0:
        if ynet['pid'][ii] not in skip:
            raise Exception(f"{ynet['pid'][ii]} in ynet but not in DB")
    else:
        row = row[0]
        df.at[row, 'ynet name'] = f"{ynet['שם פרטי'][ii]} {ynet['שם משפחה'][ii]}"
        if str(ynet['מידע על המוות'][ii]) != 'nan' and str(df['ynet story'][row]) == 'nan':
            df.at[row, 'ynet story'] = ynet['מידע על המוות'][ii]
            print(f"added ynet story to {ynet['שם פרטי'][ii]} {ynet['שם משפחה'][ii]} {ynet['מידע על המוות'][ii]}")
        df.at[row, 'ynet category'] = ynet['סיווג'][ii]
## IDF
idf = pd.read_csv('data/deaths_idf.csv')
front = pd.read_csv('data/front.csv')
for ii in range(len(idf)):
    pid = idf['pid'][ii]
    dbrow = np.where(df['pid'] == pid)[0][0]
    df.at[dbrow, 'idf story'] = idf['story'][ii]
    if str(df['ynet story'][dbrow]) != 'nan':
        front.at[ii, 'ynet'] = df['ynet story'][dbrow]
        # if str(df['idf story'][dbrow]) == 'nan':
        #     print(f"adding idf story to {df['שם פרטי'][dbrow]} {df['שם משפחה'][dbrow]} {idf['story'][ii]}")
front.to_csv('data/front.csv', index=False)
df.to_csv('data/stories.csv', index=False)


