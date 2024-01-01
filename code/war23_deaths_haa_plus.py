import pandas as pd
import os
# import Levenshtein
import numpy as np
import re


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
haa = pd.read_csv('data/deaths_haaretz.csv').iloc[::-1]
haa.reset_index(inplace=True, drop=True)
# ynet = pd.read_csv('data/ynetlist.csv')
# ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0',' ')
idf = pd.read_csv('data/deaths_idf.csv')
df = pd.read_csv('data/deaths_haaretz+.csv')
##
new = haa.iloc[np.where(haa['name'].str.contains(df['name'][len(df)-1]))[0][0]+1:]
if len(new) > 0:
    print(f'{len(new)} new victims from haaretz')
    new.reset_index(inplace=True, drop=True)
    mil = r'\([^)]*מיל[^)]*\)'
    for ii in range(len(new)):
        if new['status'][ii] == 'שוטר':
            rank = new['name'][ii].split(' ')[0]
            name = ' '.join(new['name'][ii].split(' ')[1:])
        elif new['status'][ii] == 'חייל':
            nm = new['name'][ii]
            if re.search(mil, nm):
                rank = nm[:nm.index(')')+1]
                name = nm[nm.index(')')+2:]
            else:
                rank = nm.split(' ')[0]
                name = ' '.join(new['name'][ii].split(' ')[1:])
        else:
            name = new['name'][ii]
            rank = np.nan
        story = str(new['story'][ii])
        if 'נפל ' in story or 'נרצח ' in story or 'נפטר ' in story or 'נפצע ' in story or 'נהרג ' in story:
            gender = 'M'
        elif 'נפלה ' in story or 'נרצחה ' in story or 'נפטרה ' in story:
            gender = 'F'
        else:
            gender = ''
        status = new['status'][ii]
        idf_row = np.nan
        death_date = ''
        if status == 'חייל':
            idf_row = np.where(idf['name'].str.contains(name))[0]
            if len(idf_row) == 1:
                idf_row = idf_row[0]
                death_date = idf['death_date'][idf_row]
        else:
            if len(story) > 4 and story[-1:].isdigit():
                dd = story.split(' ')[-1]
                if '-' in dd:
                    dd = dd[dd.index('-')+1:].strip()
                if dd.split('.')[0].isdigit() and dd.split('.')[1].isdigit():
                    death_date = '2023-'+dd.split('.')[1].zfill(2)+'-'+dd.split('.')[0].zfill(2)
        story = story.replace('nan', '')
        # comment
        comment = ''
        if df['status'][ii] == 'חייל' and np.isnan(df['idf_row'][ii]):
            comment += 'לא חלל; '
        elif df['status'][ii] != 'חייל' and ~np.isnan(df['idf_row'][ii]):
            comment += 'חלל; '
        konan = False
        if ~np.isnan(df['idf_row'][ii]):
            idf_name = idf['name'][df['idf_row'][ii] - 2]
            if idf_name.split(' ')[0] not in df['name'][ii]:
                raise Exception(f'{idf_name.split(" ")[0]} not in {df["name"][ii]}')
            idf_story = idf['story'][df['idf_row'][ii] - 2]
            if 'כוננות' in idf_story or 'רבש' in idf_story:
                konan = True
        else:
            idf_story = ''
        if not konan:
            if 'כוננות' in df['story'][ii] or 'רבש' in df['story'][ii]:
                konan = True
        if konan:
            comment += 'כיתת כוננות; '
        if 'חטו' in df['story'][ii] or 'נחט' in df['story'][ii]:
            kidnapped = True
        elif 'חטו' in idf_story:
            kidnapped = True
        else:
            kidnapped = False
        if kidnapped:
            comment += 'נחטף; '
        if len(comment) > 0:
            comment = comment[:-2]
        row = [name, rank, new['age'][ii], gender, new['from'][ii], status, story, idf_row + 2, death_date, comment]
        df.loc[len(df)] = row
    df.to_csv('data/deaths_haaretz+.csv', index=False)
else:
    print('no new victims from haaretz')


##
