import pandas as pd
import numpy as np
import os

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
db = pd.read_csv('data/oct7database.csv')
idf = pd.read_csv('data/deaths_idf.csv')
map = pd.read_csv('data/oct_7_9.csv')
# btl = pd.read_excel('~/Documents/btl_yael_netzer.xlsx')
kidn = pd.read_csv('data/kidnapped.csv')
def get_idx(x, vec):
    i = np.where(vec == x)[0]
    if len(i) == 0:
        i = None
    elif len(i) == 1:
        i = i[0]
    else:
        raise Exception(f'too many {x} in vec')
    return i


def intize(m):
    if (type(m) == float or type(m) == np.float64) and ~np.isnan(m):
        m = int(m)
    return m

pid = db['pid'].values
# bid = btl['Column 1'].values
##
country = []
for ii in range(len(pid)):
    row = get_idx(pid[ii], idf['pid'].values)
    if row is not None:
        country.append('ישראל')
    # elif type(db['הנצחה'][ii]) == str and 'laad' in db['הנצחה'][ii]:
    #     id = int(db['הנצחה'][ii].split('ID=')[-1])
    #     row = get_idx(id, bid)
    #     if row:
    #         age.append(intize(btl['age'][row]))
    #     else:
    #         age.append(np.nan)
    elif pid[ii] in map['pid'].values:
        row = get_idx(pid[ii], map['pid'].values)
        if 'זרים' in map['citizenGroup'][row]:
            count = map['residence'][row].strip()
            country.append(count)
            if country[ii] != db['Residence'][ii].strip():
                raise Exception(f"{ii}: {count} != {db['Residence'][ii]}")
        else:
            country.append('ישראל')
    elif pid[ii] in kidn['pid'].values:
        row = get_idx(pid[ii], kidn['pid'].values)
        if kidn['status'][row] == 'זר':
            country.append(kidn['from'][row])
        else:
            country.append('ישראל')
    else:
        country.append(np.nan)

db['Country'] = country
db.to_csv('~/Documents/country.csv', index=False)
# fixed manually
##
db = pd.read_csv('data/oct7database.csv')
zar = np.where(db['Country'] != 'ישראל')[0]
for ii in zar:
    db.at[ii, 'Residence'] = db['מקום האירוע'][ii]
##
ikidn = [x for x in range(len(db)) if db['pid'][x] in kidn['pid'].values]
for ii in range(len(db)):
    if ii in ikidn:
        krow = np.where(kidn['pid'].values == db['pid'][ii])[0][0]
        if str(db['Death date'][ii]) == 'nan':
            stat = 'kidnapped'
        else:
            if str(db['Death date'][ii])[:10] == '2023-10-07':
                if db['מקום המוות'][ii] == db['מקום האירוע'][ii]:
                    stat = 'killed; kidnapped'
                else:
                    stat = 'kidnapped; killed'
            else:
                stat = 'kidnapped; killed'
        if kidn['condition'][krow] == 'שוחרר':
            if db['pid'][ii] in [680, 809, 785, 969, 1357, 658, 654]:
                stat = stat + '; rescued'
            else:
                stat = stat + '; released'
        elif kidn['condition'][krow] == 'הוחזר':
            stat = stat + '; retrieved'
    else:
        stat = 'killed'
    db.at[ii, 'Status'] = stat
##
party = {'nan': np.nan, 'פסטיבל נובה': 'Nova', 'מסיבת פסיידאק': 'Psyduck', 'מידברן': np.nan}
for ii in range(len(db)):
    if db['pid'][ii] in map['pid'].values:
        mrow = np.where(map['pid'].values == db['pid'][ii])[0][0]
        db.at[ii, 'Party'] = party[str(map['comment'][mrow])]
    else:
        db.at[ii, 'Party'] = np.nan

##
dbl = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
sus = np.zeros(len(dbl), bool)
for ii in range(len(dbl)):
    if db['מקום האירוע'][ii] == 'פסטיבל נובה' and str(dbl['event_coordinates'][ii])[:2] != '31':
        if str(db['מקום המוות'][ii]) != 'nan':
            sus[ii] = True
dbs = dbl[sus]
dbs.to_excel('~/Documents/sus.xlsx', index=False)
##
db = pd.read_csv('data/oct7database.csv')
kidn = pd.read_csv('data/kidnapped.csv')
ikidn = [x for x in range(len(db)) if db['pid'][x] in kidn['pid'].values]
nova = np.where(db['Event location (oct7map)'] == 'Nova')[0]
rep = [x for x in nova if x in ikidn]
for ii in rep:
    if str(db['Party'][ii]) == 'nan':
        db.at[ii, 'Party'] = 'Nova'

##
db = pd.read_csv('data/oct7database.csv')
map = pd.read_csv('data/oct_7_9.csv')
keys = ['אזרחים', 'אזרחים זרים', 'כבאות והצלה', 'כיתות כוננות','מגן דוד אדום',
        'משטרה', "משטרה (מיל')", 'צה"ל', 'צה"ל (מיל\')', 'שב"כ']
vals = ['אזרח', 'אזרח', 'כבאי', 'כיתת כוננות', 'מד"א',
        'שוטר', 'שוטר', 'חייל', 'חייל', 'שב"כ']
reform = dict(zip(keys, vals))

for ii in range(len(map)):
    role = reform[map['citizenGroup'][ii]]
    row = np.where(db['pid'] == map['pid'][ii])[0][0]
    db.at[row, 'Role'] = role

for ii in range(len(db)):
    if db['pid'][ii] not in map['pid'].values and '.idf.' in str(db['הנצחה'][ii]):
        db.at[ii, 'Role'] = 'חייל'
    # if role[-1] == 'מד"א':
    #     try:
    #         print(str(ii) + ' ' + str(db['pid'][row]) + '    ' + db["הנצחה"][row][:20])
    #     except:
    #         print(str(ii) + ' ' + str(db['pid'][row]) + '    ' + str(db["הנצחה"][row]))

