import pandas as pd
import os
import json
import time
import requests
import numpy as np



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
    'Gender': 'genderHe',
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
            value = ''
        record[db2api[key]] = value
    record['statusEn'] = [s.strip() for s in record['statusEn'].split(';')]
    return record
if __name__ == '__main__':
    pid = db['pid'].values[-1]
    record = pid2record(pid)
    record['pid'] = 'test001'
    with open('record_dump.json', 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    send_records(record)
    print('done')
    time.sleep(1)
