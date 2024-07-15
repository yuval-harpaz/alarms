import pandas as pd
import os
# import Levenshtein
import numpy as np
import re


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
##
haa = pd.read_csv('data/deaths_haaretz.csv').iloc[::-1]
haa.reset_index(inplace=True, drop=True)
# ynet = pd.read_csv('data/ynetlist.csv')
# ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0',' ')
idf = pd.read_csv('data/deaths_idf.csv')
df = pd.read_csv('data/deaths_haaretz+.csv')
##
last_name = df['name'][len(df)-1]
where_last = np.where(haa['name'].str.contains(last_name))[0]
if len(where_last) == 0:
    print('haa+ waiting for '+last_name)
else:
    new = haa.iloc[where_last[-1]+1:]
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
                    idf_row = idf_row[0] + 2
                    death_date = idf['death_date'][idf_row - 2]

            else:
                if len(story) > 4 and story[-1:].isdigit():
                    dd = story.split(' ')[-1]
                    if '-' in dd:
                        dd = dd[dd.index('-')+1:].strip()
                    if dd.split('.')[0].isdigit() and dd.split('.')[1].isdigit():
                        death_date = '2024-'+dd.split('.')[1].zfill(2)+'-'+dd.split('.')[0].zfill(2)
            story = story.replace('nan', '')
            # comment
            comment = ''
            print(ii)
            # idf_row = df['idf_row'][ii]
            if type(idf_row) == str:
                idf_row = float(idf_row)
            if new['status'][ii] == 'חייל' and np.isnan(idf_row):
                comment += 'לא חלל; '
            elif new['status'][ii] != 'חייל' and ~np.isnan(idf_row):
                comment += 'חלל; '
            konan = False
            if ~np.isnan(idf_row):
                idf_name = idf['name'][idf_row - 2]
                if idf_name.split(' ')[0] not in new['name'][ii]:
                    raise Exception(f'{idf_name.split(" ")[0]} not in {df["name"][ii]}')
                idf_story = idf['story'][idf_row - 2]
                if 'כוננות' in idf_story or 'רבש' in idf_story:
                    konan = True
            else:
                idf_story = ''
            sty = str(new['story'][ii])
            if not konan:
                if 'כוננות' in sty or 'רבש' in sty:
                    konan = True
            if konan:
                comment += 'כיתת כוננות; '
            if 'חטו' in sty or 'נחט' in sty:
                kidnapped = True
            elif 'חטו' in idf_story:
                kidnapped = True
            else:
                kidnapped = False
            if kidnapped:
                comment += 'נחטף; '
            if len(comment) > 0:
                comment = comment[:-2]
            row = [name, rank, new['age'][ii], gender, new['from'][ii], status, story, idf_row, death_date, comment, np.nan, np.nan]
            df.loc[len(df)] = row
        df.to_csv('data/deaths_haaretz+.csv', index=False)
    else:
        print('no new victims from haaretz')


## update by-year list
df = pd.read_csv('data/deaths_haaretz+.csv')
idf = pd.read_csv('data/deaths_idf.csv')
yearly = pd.read_csv('data/deaths_by_year.csv')
isidf = ~df['idf_row'].isnull().values
row = df['idf_row'].values[isidf]
if len(row) > len(np.unique(row)):
    n = np.unique([x for x in row if len(np.where(row == x)[0]) > 1])
    print('duplicates!' + str(n))
rng = np.arange(2, len(idf)+2)
missing = [x for x in rng if x not in row]
if len(missing) > 0:
    print('missing idf row: '+str(missing)[1:-1])
year = df['death_date'].values.astype(str)
for ii in range(len(year)):
    yy = year[ii]
    if len(yy) > 4:
        year[ii] = yy[:4]
for yr in [2023, 2024]:
    yrow = np.where(yearly['year'] == yr)[0][0]
    soldiers = np.sum(isidf & (year == str(yr)))
    civil = np.sum(~isidf & (year == str(yr)))
    if yr == 2023:  # deaths before 7/10
        soldiers += 55
        civil += 34
    yearly.at[yrow, 'armed_forces'] = soldiers
    yearly.at[yrow, 'civilians'] = civil
yearly.to_csv('data/deaths_by_year.csv', index=False)