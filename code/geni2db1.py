import pandas as pd
import numpy as np
import os
from urllib.parse import unquote

geni = pd.read_csv('~/Documents/geni-export-list.csv')
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
db = db[~db['הנצחה'].isnull()]
db.reset_index(inplace=True, drop=True)
about = geni['About'].astype(str).apply(unquote)
for ii in range(len(db)):
    han = unquote(str(db['הנצחה'][ii]))
    if len(han) > 3:  # not nan
        geni_row = np.where(about.str.contains(han, regex=False))[0]
        if len(geni_row) == 1:
            db.at[ii, 'geni'] = geni['URL'][geni_row[0]]
            geni.at[geni_row[0], 'oct7database'] = ';'.join(list(db.loc[ii].astype(str).values[:9])).replace('nan','')
geni.to_excel('~/Documents/geni_pid.xlsx', index=False)
cols = ['pid', 'first name', 'last name', 'middle name', 'nickname', 'שם פרטי', 'שם משפחה', 'שם נוסף', 'כינוי', 'geni']
db[cols].to_csv('~/Documents/db_geni.csv', index=False)

## second pass, identify by name
geni = pd.read_excel('~/Documents/geni_pid.xlsx')
db = pd.read_csv('~/Documents/db_geni.csv')

def is_hebrew(text):
    return any('\u0590' <= c <= '\u05FF' for c in str(text))
empty = np.where(geni['oct7database'].isna())[0]
for ig in empty:# already matched
    name = str(geni['Name'][ig])
    first = str(geni['First Name'][ig]).strip()
    last = str(geni['Last Name'][ig]).strip()
    mask = (db['first name'] == first) & \
           (db['last name'].astype(str).str.strip() == last)
    db_rows = np.where(mask & db['geni'].isna())[0]
    if len(db_rows) == 1:
        idb = db_rows[0]
        db.at[idb, 'geni'] = geni['URL'][ig]
        geni.at[ig, 'oct7database'] = ';'.join(
            [str(db[c][idb]) for c in db.columns[:9]]
        ).replace('nan', '')
print(np.sum(geni['oct7database'].isnull()))

geni.to_excel('~/Documents/geni_pid.xlsx', index=False)
db.to_csv('~/Documents/db_geni.csv', index=False)

## allow first split to match
geni = pd.read_excel('~/Documents/geni_pid.xlsx')
db = pd.read_csv('~/Documents/db_geni.csv')

def is_hebrew(text):
    return any('\u0590' <= c <= '\u05FF' for c in str(text))
empty = np.where(geni['oct7database'].isna())[0]
for ig in empty:# already matched
    name = str(geni['Name'][ig])
    first = str(geni['First Name'][ig]).split(' ')[0].strip()
    last = str(geni['Last Name'][ig]).split(' ')[0].strip()
    mask = (db['first name'] == first) & \
           (db['last name'].astype(str).str.strip() == last)
    db_rows = np.where(mask & db['geni'].isna())[0]
    if len(db_rows) == 1:
        idb = db_rows[0]
        db.at[idb, 'geni'] = geni['URL'][ig]
        geni.at[ig, 'oct7database'] = ';'.join(
            [str(db[c][idb]) for c in db.columns[:9]]
        ).replace('nan', '')
print(np.sum(geni['oct7database'].isnull()))

geni.to_excel('~/Documents/geni_pid.xlsx', index=False)
db.to_csv('~/Documents/db_geni.csv', index=False)



## find Hebrew name match in html

geni = pd.read_excel('~/Documents/geni_pid.xlsx')
db = pd.read_csv('~/Documents/db_geni.csv')
html_file = 'Geni - _חללי מלחמת _חרבות ברזל - Victims of _Iron Swords_ War Project.html'
with open(os.path.expanduser(f'~/Documents/{html_file}'), 'r', encoding='utf-8') as f:
    html_str = f.read()
https = html_str.split('https://www.geni.com/people/')
df = pd.DataFrame(columns=['Name', 'URL'])
ip = -1
for seg in https:
    ip += 1
    if seg[:7] == 'private':
        url = 'https://www.geni.com/people/' + seg.split('"')[0]
        name = seg.split('>')[2].split('<')[0]
        dflen = len(df)
        df.at[dflen, 'Name'] = name
        df.at[dflen, 'URL'] = url
df['Name'] = df['Name'].str.replace('(פרופיל פרטי)', '')
df['Name'] = df['Name'].str.strip()
df.drop_duplicates(inplace=True)
df.reset_index(inplace=True, drop=True)

empty = np.where(geni['oct7database'].isna())[0]
for ig in empty:
    html_str.index(f"{geni['First Name'][ig]}-{geni['Last Name'][ig]}")

for ig in empty:# already matched
    name = str(geni['Name'][ig])
    first = str(geni['First Name'][ig]).split(' ')[0].strip()
    last = str(geni['Last Name'][ig]).split(' ')[0].strip()
    mask = (db['first name'] == first) & \
           (db['last name'].astype(str).str.strip() == last)
    db_rows = np.where(mask & db['geni'].isna())[0]
    if len(db_rows) == 1:
        idb = db_rows[0]
        db.at[idb, 'geni'] = geni['URL'][ig]
        geni.at[ig, 'oct7database'] = ';'.join(
            [str(db[c][idb]) for c in db.columns[:9]]
        ).replace('nan', '')
print(np.sum(geni['oct7database'].isnull()))

geni.to_excel('~/Documents/geni_pid.xlsx', index=False)
db.to_csv('~/Documents/db_geni.csv', index=False)