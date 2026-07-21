import pandas as pd
import os
import json
import time
import requests
import numpy as np
from selenium.webdriver.common.devtools.v143.fetch import continue_request

local = '/home/yuval/alarms/'
if os.path.isdir(local):
    os.chdir(local)
elif os.path.isdir(local.replace('yuval', 'innereye')):
    os.chdir(local.replace('yuval', 'innereye'))
##
db2api = {
    'first name': 'firstNameEn',
    'last name': 'lastNameEn',
    'middle name': 'middleNameEn',
    'nickname': 'nicknameEn',
    'שם פרטי': 'firstNameHe',
    'שם משפחה': 'lastNameHe',
    'שם נוסף': 'middleNameHe',
    'כינוי': 'nicknameHe',
    'Gender': 'genderEn',
    'Age': 'age',
    'Residence': 'residenceHe',
    'Country': 'countryHe',
    'Role': 'roleHe',
    'Party': 'party',
    'Status': 'statusEn',
    'Event date': 'eventDate',
    'Death date': 'deathDate',
    'מקום האירוע': 'eventLocationHe',
    'מקום המוות': 'deathLocationHe',
    'front': 'frontEn',
    'סיבת המוות': 'causeOfDeathHe',
    'הנצחה': 'memorialSite',
    'הספריה הלאומית': 'nationalLibrary',
    'Event location': 'eventLocationEn',
    'Death location': 'deathLocationEn'
}
api2db = {v: k for k, v in db2api.items()}

require_translation = {'genderEn': 'genderHe',
                       'residenceHe': 'residenceEn',
                       'countryHe': 'countryEn',
                       'roleHe': 'roleEn',
                       'statusEn': 'statusHe',
                       'frontEn': 'frontHe',
                       'causeOfDeathHe': 'causeOfDeathEn'}

def check_translation(save_to='data/dictionaries.json'):
    downloaded = {'En': pd.read_csv('~/Documents/oct7_database_en.csv'), 'He': pd.read_csv('~/Documents/oct7_database.csv')}
    dictionary = {}
    for field in require_translation.keys():
        dictionary[field] = {}
        en_title = api2db[field].replace('front', 'Front')
        en_title = en_title.replace('סיבת המוות', 'Cause of Death')
        icolumn = np.where(np.array(downloaded['En'].keys()) == en_title)[0][0]
        existing_values = downloaded[field[-2:]].iloc[:, icolumn].unique()
        for ev in existing_values:
            if str(ev) == 'nan':
                continue
            isev = downloaded[field[-2:]].iloc[:, icolumn].values == ev
            other_language = ['He' if field[-2:] == 'En' else 'En'][0]
            translated = np.unique(downloaded[other_language].iloc[:, icolumn].values[isev])
            if len(translated) == 1:
                dictionary[field][ev] = translated[0]
            else:
                dictionary[field][ev] = translated
    if type(save_to) == str:
        with open(save_to, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=2)
    return dictionary


API_URL = os.environ['OCT7URL']
API_KEY = os.environ['OCT7KEY']
def send_records(records):
    response = requests.post(
        API_URL,
        json=records,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        }
    )
    response.raise_for_status()
    return response.json()
db = pd.read_csv('https://raw.githubusercontent.com/yuval-harpaz/alarms/refs/heads/master/data/oct7database.csv', dtype={'הספריה הלאומית': str})
with open('data/dictionaries.json') as f:
    dictionary = json.load(f)

def pid2record(pid):
    row = np.where(db['pid'] == pid)[0]
    if len(row) == 1:
        row = row[0]
    else:
        print(f"pid {pid} not found")
        return None
    record = {'pid': str(int(pid))}
    for key in db2api.keys():
        value = db.at[row, key]
        if str(value) == 'nan':
            # value = ''
            continue
        record[db2api[key]] = value
    record['statusEn'] = [s.strip() for s in record['statusEn'].split(';')]
    if 'nationalLibrary' in record.keys():
        record['nationalLibrary'] = 'https://www.nli.org.il/he/authorities/' + record['nationalLibrary']
    for key, translated_key in require_translation.items():
        value = db.at[row, api2db[key]]
        if str(value) == 'nan':
            continue
        # if key == 'causeOfDeathHe':
        #     print('debug')
        translated_value = dictionary[key][value]
        record[translated_key] = translated_value
    record['statusHe'] = [s.strip() for s in record['statusHe'].split(';')]
    return record
    # if str(db.at[row, 'הנצחה']) == 'nan':
    #     continue
    # else:

if __name__ == '__main__':
    # pid = db['pid'].values[-1]
    pid = 52
    record = pid2record(pid)
    record['pid'] = 'test005'
    with open('record_dump.json', 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    resp = send_records(record)
    print(resp)
    time.sleep(1)
