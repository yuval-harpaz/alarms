import pandas as pd
import os
import json
import time
import requests
import numpy as np
# from selenium.webdriver.common.devtools.v143.fetch import continue_request

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

def get_records(pids):
    if type(pids) == int:
        pids = [pids]
    response = requests.post(
        API_URL.replace('addRecord', 'getRecord'),
        # json={'pids': [int(pid) for pid in pids]},
        json={"pids":pids},
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        }
    )
    response.raise_for_status()
    return response.json()

COLUMNS_URL = API_URL.replace('addRecords', 'getColumns').replace('addRecord', 'getColumns')
def get_columns(fields):
    """the values of specific fields for every record on the website"""
    if type(fields) == str:
        fields = [fields]
    response = requests.post(
        COLUMNS_URL,
        json={"fields": fields},
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        }
    )
    response.raise_for_status()
    return response.json()

def allowed_columns():
    """getColumns lists the fields it serves when asked for a field it doesn't know"""
    response = requests.post(
        COLUMNS_URL,
        json={"fields": ["which fields are allowed?"]},
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        }
    )
    return response.json()['allowed']

EMPTY = ''  # what addRecords takes as a delete, try None if empty strings are ignored
MAX_PIDS = 500  # getRecords refuses more than that in one request
def website_pid():
    """all the pids on the website"""
    return [rec['pid'] for rec in get_columns(['pid'])['records']]

def get_all_records(pids=None, chunk=MAX_PIDS, tries=3):
    """the whole website, record by record, in chunks of pids. the API drops a request now and then,
    so every chunk is asked for again before giving up"""
    if pids is None:
        pids = website_pid()
    records = []
    not_found = []
    for start in range(0, len(pids), chunk):
        batch = [int(p) for p in pids[start:start + chunk]]
        for itry in range(tries):
            try:
                response = get_records(batch)
                break
            except Exception as exc:
                if itry == tries - 1:
                    raise
                print(f'getRecords failed for pid {batch[0]}-{batch[-1]} ({exc}), asking again')
                time.sleep(5)
        records.extend(response['records'])
        not_found.extend(response['notFound'])
    return records, not_found

CSV_URL = 'https://raw.githubusercontent.com/yuval-harpaz/alarms/refs/heads/master/data/oct7database.csv'
db = pd.read_csv(CSV_URL, dtype={'הספריה הלאומית': str})


def csv_diff(path='data/oct7database.csv'):
    """pid where the local oct7database.csv is not the same as the one on github,
    which is the one pid2record reads. anything not committed and pushed is invisible here"""
    if not os.path.isfile(path):
        print(path + ' not found, comparing to github is not possible')
        return []
    lines = []
    with open(path, encoding='utf-8') as f:
        local_txt = f.read()
    for txt in [local_txt, requests.get(CSV_URL).text]:
        by_pid = {}
        for line in txt.split('\n')[1:]:
            if len(line.strip()) > 0:
                by_pid[line.split(',')[0]] = line
        lines.append(by_pid)
    pids = set(list(lines[0].keys()) + list(lines[1].keys()))
    return sorted([p for p in pids if lines[0].get(p) != lines[1].get(p)])
with open('data/dictionaries.json') as f:
    dictionary = json.load(f)

# wix shows a memorial site type, which is not a column of the csv but follows the domain of the הנצחה url
memorial_types = {'laad.btl.gov.il': ['National Insurance (Civilians)', 'ביטוח לאומי (אזרחים)'],
                  'www.idf.il': ['IDF Fallen', 'חללי צה"ל'],
                  'lezichram.police.gov.il': ['Israel Police', 'משטרת ישראל'],
                  'www.shabak.gov.il': ['Shin Bet', 'שב"כ'],
                  'www.izkor.gov.il': ['Yizkor', 'יזכור'],
                  'www.gov.il': ['Foreign Affairs', 'משרד החוץ']}
no_memorial = ['None', 'ללא']  # no url at all
other_memorial = ['Other', 'אחר']  # a url with a domain which is not listed above


def memorial_type(url):
    """the memorial site type, by the domain of the הנצחה url"""
    if url is None or str(url) == 'nan' or '/' not in str(url):
        return no_memorial
    return memorial_types.get(str(url).split('/')[2], other_memorial)


def pid2record(pid):
    row = np.where(db['pid'] == pid)[0]
    if len(row) == 1:
        row = row[0]
    else:
        print(f"pid {pid} not found")
        return None
    record = {'pid': int(pid)}
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
    record['memorialSiteTypeEn'], record['memorialSiteTypeHe'] = memorial_type(record.get('memorialSite'))
    return record
    # if str(db.at[row, 'הנצחה']) == 'nan':
    #     continue
    # else:


def same_value(csv_value, website_value, date=False):
    """compare one value of oct7database.csv with the value on the website,
    ignoring the way lists are stored and numbers and dates are formatted"""
    if csv_value is None or str(csv_value).strip() in ['nan', '']:
        return website_value is None or str(website_value).strip() in ['nan', '']
    if website_value is None or str(website_value).strip() in ['nan', '']:
        return False
    if date:
        return pd.to_datetime(csv_value) == pd.to_datetime(website_value)
    numbers = [v for v in [csv_value, website_value] if isinstance(v, (int, float, np.integer, np.floating))]
    if len(numbers) > 0:  # Age is a float in the csv and an int on the website
        try:
            return float(csv_value) == float(website_value)
        except ValueError:
            return False
    listed = []
    for value in [csv_value, website_value]:
        if type(value) != list:
            value = str(value).split(';')
        listed.append([str(x).strip() for x in value])
    return listed[0] == listed[1]


def show(value):
    """quote the value when it has spaces around it, otherwise it is invisible in a report"""
    if type(value) == str and (value.strip() != value or value in ['None', 'nan', '']):
        return f'"{value}"'
    return str(value)


def missing_pid(pids=None):
    """pid in oct7database.csv with no record on the website"""
    if pids is None:
        pids = website_pid()
    return [int(p) for p in db['pid'].values if int(p) not in pids]


def extra_pid(pids=None):
    """pid on the website which is not in oct7database.csv"""
    if pids is None:
        pids = website_pid()
    return [int(p) for p in pids if p not in db['pid'].values]


def changed_pid(verbose=False, records=None, clear=True):
    """the fields which differ between oct7database.csv and the website, per pid.
    a field which has a value on the website and none in the csv is sent as an empty string,
    which is the way to delete it. clear=False leaves such fields as they are"""
    if records is None:
        records, not_found = get_all_records()
    csv_fields = list(db2api.values()) + list(require_translation.values())
    changed = {}
    for rec in records:
        pid = rec['pid']
        record = pid2record(pid)
        if record is None:  # on the website but not in the csv, see extra_pid
            continue
        tochange = {'pid': pid}
        for field, value in record.items():
            if field == 'pid':
                continue
            if not same_value(value, rec.get(field), date=field.endswith('Date')):
                if verbose:
                    print(f'pid {pid} {field}: website has {show(rec.get(field))}, csv has {show(value)}')
                tochange[field] = value
        if clear:
            for field in csv_fields:
                if field not in record.keys() and str(rec.get(field)) not in ['None', 'nan', '']:
                    if verbose:
                        print(f'pid {pid} {field}: website has {show(rec.get(field))}, csv has nothing')
                    tochange[field] = EMPTY
        if len(tochange) > 1:
            changed[pid] = tochange
    return changed


if __name__ == '__main__':
    pid = 764
    changed = changed_pid()
    send_records(changed[pid])
    # record = pid2record(pid)


    # record['pid'] = 'test005'
    # with open('record_dump.json', 'w', encoding='utf-8') as f:
    #     json.dump(record, f, ensure_ascii=False, indent=2)
    # resp = send_records(record)
    # print(resp)
    # time.sleep(1)
