"""Improved version of war23_nli_scrape.py. First syncs ~/Documents/nli.csv with oct7database.csv:
adds missing pids and detects NLI ID conflicts between the two sources. Then opens the NLI authority page
for each relevant pid (either all with an ID, or only those not yet scraped), extracts the name from
'item_collections', computes Levenshtein distance against the database name, and checks the Harpaz_ID
and 1Source_ID (some entries have one or both). Flags issues ('Name mismatch', 'Wrong Harpaz ID',
'Wrong 1Source ID', 'English name', etc.) and saves incrementally to ~/Documents/nli.csv.
Important, the script currently fails the robot test by cloudflair. when using my personal chrome it may pass but the script hangs
"""
## compare the NLI 710 identities list (Aug 2026) with oct7database, save mismatches to ~/Documents/nli710_issues.csv
import pandas as pd
import os
import numpy as np
import re
import Levenshtein

for home in ['innereye', 'yuval']:
    if os.path.isdir('/home/'+home+'/alarms/'):
        os.chdir('/home/'+home+'/alarms/')
        break

nli710 = pd.read_csv(os.path.expanduser("~/Documents/אוג' 2026 רשימת זהויות 710 של הספרייה - גיליון ללא פונקציות.csv"),
                     dtype={'MMS ID': str})
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
db_ids = db['הספריה הלאומית'].astype(str).str.strip()


def normalize(name):
    name = '' if pd.isna(name) else str(name)
    name = name.replace('׳', "'").replace('״', '"').replace('-', ' ')
    name = re.sub(r'[֑-ׇ]', '', name)  # remove niqqud
    return name.strip()


def db_name(row, eng=False):
    cols = ['first name', 'middle name', 'last name', 'nickname'] if eng else ['שם פרטי', 'שם נוסף', 'שם משפחה', 'כינוי']
    return ' '.join([normalize(db[col][row]) for col in cols]).replace('  ', ' ').strip()


def name_distance(tokens_nli, row, eng=False):
    # word order and middle names differ between the sources, so match each NLI word
    # to its closest db name part, allowing one Levenshtein mistake in total
    tokens_db = db_name(row, eng).lower().split()
    if len(tokens_nli) == 0 or len(tokens_db) == 0:
        return 99
    return sum([min([Levenshtein.distance(t, d) for d in tokens_db]) for t in tokens_nli])


issues = []
not_in_db = []  # [nli_id, first, last, tokens, eng]
for ii in range(len(nli710)):
    nli_id = str(nli710['MMS ID'][ii]).strip()
    first_nli = normalize(nli710['שם פרטי בעברית'][ii])
    last_nli = normalize(nli710['שם משפחה בעברית'][ii])
    eng = first_nli == '' and last_nli == ''
    if eng:  # no Hebrew name, parse the English name from the title, e.g. "Joshi, Bipin, 2000-2023"
        parts = [p.strip() for p in str(nli710['title'][ii]).split('\n')[0].split(',')]
        parts = [p for p in parts if p != '' and re.search(r'\d', p) is None]
        last_nli = parts[0] if len(parts) > 0 else ''
        first_nli = parts[1] if len(parts) > 1 else ''
    tokens_nli = (first_nli + ' ' + last_nli).lower().split()
    db_row = np.where(db_ids == nli_id)[0]
    if len(db_row) == 0:
        not_in_db.append([nli_id, first_nli, last_nli, tokens_nli, eng])
    elif name_distance(tokens_nli, db_row[0], eng) > 1:
        issues.append([nli_id, first_nli, last_nli, db_name(db_row[0], eng), 'name mismatch'])
# db IDs missing from the NLI list, before checking for conflicting IDs per name
nli_ids = set(nli710['MMS ID'].astype(str).str.strip())
missing_db = [ii for ii in np.where(db['הספריה הלאומית'].notna())[0] if db_ids[ii] not in nli_ids]
# NLI IDs not found in db: look for the same name under a different ID (like ביפין ג'ושי)
for nli_id, first_nli, last_nli, tokens_nli, eng in not_in_db:
    conflict = [ii for ii in missing_db if name_distance(tokens_nli, ii, eng) <= 1]
    if len(conflict) == 0:
        issues.append([nli_id, first_nli, last_nli, '', 'ID in NLI not found in oct7database'])
    else:
        issues.append([nli_id, first_nli, last_nli, db_name(conflict[0], eng),
                       'ID in NLI not found in oct7database, oct7database ID: ' + db_ids[conflict[0]]])
        missing_db.remove(conflict[0])
for ii in missing_db:
    name = (str(db['שם פרטי'][ii]) + ' ' + str(db['שם משפחה'][ii])).replace('nan', '').strip()
    issues.append([db_ids[ii], '', '', name, 'ID in oct7database not found in NLI'])
issues = pd.DataFrame(issues, columns=['nli_id', 'שם פרטי', 'שם משפחה', 'oct7db name', 'comment'])
issues['link'] = 'https://www.nli.org.il/he/authorities/' + issues['nli_id']
issues.to_csv(os.path.expanduser('~/Documents/nli710_issues.csv'), index=False)
print(issues['comment'].str.split(',').str[0].value_counts())

## get Hebrew and English names and death date from VIAF for every NLI ID in oct7database, saved to ~/Documents/viaf.csv
# VIAF mirrors the NLI (J9U) authority records and is not behind cloudflare, e.g.
# https://viaf.org/viaf/sourceID/J9U%7C987012802839705171 (ניתאי עמאר). Runs incrementally, skips IDs already in viaf.csv.
import pandas as pd
import os
import numpy as np
import re
import requests
import time

for home in ['innereye', 'yuval']:
    if os.path.isdir('/home/'+home+'/alarms/'):
        os.chdir('/home/'+home+'/alarms/')
        break


def parse_viaf(data):
    """extract names, dates and viaf id from the VIAF json (both 'heb' and 'lat' headings share the same J9U record)"""
    cluster = data['ns1:VIAFCluster']
    out = {'viaf_id': str(cluster.get('ns1:viafID', '')), 'name_heb': '', 'name_eng': '', 'dates': '',
           'birth_date': str(cluster.get('ns1:birthDate', '')), 'death_date': str(cluster.get('ns1:deathDate', ''))}
    for key in ['birth_date', 'death_date']:
        if out[key] == '0':  # VIAF puts 0 for unknown dates
            out[key] = ''
    headings = cluster.get('ns1:mainHeadings', {}).get('ns1:mainHeadingEl', [])
    if isinstance(headings, dict):  # a single heading is not wrapped in a list
        headings = [headings]
    for heading in headings:
        subfields = heading.get('ns1:datafield', {}).get('ns1:subfield', [])
        if isinstance(subfields, dict):
            subfields = [subfields]
        subfields = {str(sf['code']): str(sf['content']).strip() for sf in subfields}
        name = subfields.get('a', '').strip(' ,')
        if re.search(r'[א-ת]', name):
            out['name_heb'] = name
        elif name != '':
            out['name_eng'] = name
        if 'd' in subfields:
            out['dates'] = subfields['d'].strip(' ,.')
    return out


db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
viaf_path = os.path.expanduser('~/Documents/viaf.csv')
viaf_columns = ['pid', 'nli_id', 'viaf_id', 'name_heb', 'name_eng', 'dates', 'birth_date', 'death_date', 'status']
if os.path.isfile(viaf_path):
    viaf = pd.read_csv(viaf_path, dtype={'nli_id': str, 'viaf_id': str})
    viaf = viaf[viaf['status'].isin(['ok', 'http 404'])].reset_index(drop=True)  # retry rate limited / failed requests
else:
    viaf = pd.DataFrame(columns=viaf_columns)
rows = np.where(db['הספריה הלאומית'].notna())[0]
for ii in rows:
    nli_id = db['הספריה הלאומית'][ii].strip()
    if nli_id in viaf['nli_id'].values:
        continue
    print(db['pid'][ii], nli_id)
    result = {'viaf_id': '', 'name_heb': '', 'name_eng': '', 'dates': '', 'birth_date': '', 'death_date': ''}
    try:
        for attempt in range(5):
            resp = requests.get('https://viaf.org/viaf/sourceID/J9U%7C' + nli_id, headers={'Accept': 'application/json'}, timeout=30)
            if resp.status_code != 429:
                break
            wait = int(resp.headers.get('Retry-After', 60))  # VIAF rate limit, about 1000 requests before 429
            print(f'rate limited, waiting {wait}s')
            time.sleep(wait)
        if resp.status_code != 200:
            status = 'http ' + str(resp.status_code)
        elif 'json' not in resp.headers.get('content-type', ''):
            status = 'not json'
        else:
            result = parse_viaf(resp.json())
            status = 'ok'
    except Exception as err:
        status = 'error: ' + str(err)[:100]
    viaf.loc[len(viaf)] = [db['pid'][ii], nli_id, result['viaf_id'], result['name_heb'], result['name_eng'],
                           result['dates'], result['birth_date'], result['death_date'], status]
    viaf.to_csv(viaf_path, index=False)  # save incrementally
    time.sleep(1)
print(viaf['status'].value_counts())

## scrape NLI authority pages
import pandas as pd
import os
import numpy as np
from selenium import webdriver
import re
import Levenshtein
# import requests
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import undetected_chromedriver as uc



local = ''
for home in ['innereye', 'yuval']:
    local = '/home/'+home+'/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        break


# url = 'https://www.nli.org.il/he/search?projectName=NLI#&q=any,contains,FIRST%20LAST&bulkSize=30&index=0&sort=rank&multiFacets=facet_local18,include,2023,1|,|facet_local18,include,2024,1|,|facet_local18,include,2025,1&t=authorities'
# fill missing IDs from db
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
nli_path = os.path.expanduser('~/Documents/nli.csv')
nli_columns = ['nli_id', 'pid', 'harpaz_id', 'name', 'first_nli', 'last_nli', 'years', 'issues', '1source_id']
if os.path.isfile(nli_path):
    nli = pd.read_csv(nli_path, dtype={'nli_id': str, 'issues': str})
    for col in nli_columns:
        if col not in nli.columns:
            nli[col] = np.nan
else:
    nli = pd.DataFrame(columns=nli_columns)
# got_id = np.where(db['הספריה הלאומית'].notna())[0]
for ii in range(len(db)):
    row_nli = np.where(nli['pid'] == db['pid'][ii])[0]
    if len(row_nli) == 0:
        name = db['שם פרטי'][ii].strip() + ' ' + str(db['שם נוסף'][ii]).strip() + ' ' + db['שם משפחה'][ii].strip() + ' ' + str(db['כינוי'][ii]).strip()
        name = name.replace('nan', '').replace('  ', ' ').strip()
        new_row = [db['הספריה הלאומית'][ii], db['pid'][ii], np.nan, name, np.nan, np.nan, np.nan, np.nan, np.nan]
        nli.loc[len(nli)] = new_row
        row_nli = len(nli)-1
    else:
        row_nli = row_nli[0]
    if str(db['הספריה הלאומית'][ii]) == 'nan':
        nli.at[ii, 'issues'] = 'No ID'
    else:
        id_nli = db['הספריה הלאומית'][ii]
        if str(nli['nli_id'][row_nli]) == 'nan':
            nli.at[row_nli, 'nli_id'] = id_nli
        elif str(nli['nli_id'][row_nli]) != id_nli:
            print(f'Conflict for pid {db["pid"][ii]}: prev {nli["nli_id"][row_nli]} current {id_nli}')
            nli.at[row_nli, 'nli_id'] = id_nli
            nli.at[row_nli, 'issues'] = 'ID conflict'
nli.to_csv(nli_path, index=False)
input_resp = input('search existing? (y/n): ')
if input_resp == 'y':
    id_to_scan = db['pid'][db['הספריה הלאומית'].notna()].values
else:
    id_to_scan = nli['pid'][nli['first_nli'].isna() & nli['nli_id'].notna()].values

rows = [i for i in range(len(nli)) if nli['pid'][i] in id_to_scan]
pattern = 'item_collections'
# chrome_options = uc.ChromeOptions()
# chrome_options.add_argument("user-data-dir=/home/innereye/.config/google-chrome")  # e.g. ~/.config/google-chrome
# chrome_options.add_argument("profile-directory=Default")
# options.add_argument("--user-data-dir=/tmp/testprofile")
# options.add_argument("--user-data-dir=/home/yuval/.config/google-chrome")
# browser = webdriver.Chrome()
# browser.get("about:blank")
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={os.environ['HOME']}/.config/chrome-selenium")
options.add_argument("--profile-directory=Default")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
browser = webdriver.Chrome(options=options)
browser.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    }
)
browser.get('https://www.nli.org.il/he')  # manually confirm not a bot
ip = input('Press Enter to continue...')
for ii in rows:  # [427] :
    print('pid', nli['pid'][ii])
    db_row = np.where(db['pid'] == nli['pid'][ii])[0][0]
    personal = 'https://www.nli.org.il/he/authorities/'+nli['nli_id'][ii]
    browser.get(personal)
    htmlp = browser.page_source
    # find item-collections in htmlp
    results = re.search(pattern, htmlp)
    if results is None:
        print(f'No item_collections for {db["pid"].values[ii]}')
    else:
        results_section = htmlp[htmlp.index(pattern) + len(pattern)+2:]
        name = results_section[:results_section.index('<')]
        names = [n.strip() for n in name.split(',')]
        name_db = db['שם משפחה'][db_row].strip() + ',' + db['שם פרטי'][db_row].strip() + ',' + str(db['שם נוסף'][db_row]).strip() + ',' + str(db['כינוי'][db_row]).strip()
        first = ''
        last = ''
        issues = ''
        if len(names) == 0:
            nli.at[ii, 'issues'] = 'No name found'
        else:
            last = names[0]
            nli.at[ii, 'last_nli'] = last
            distance = min([Levenshtein.distance(last, n.strip()) for n in name_db.split(',')])
            if len(names) > 1:
                first = names[1]
                nli.at[ii, 'first_nli'] = first
                distance = min([distance, min([Levenshtein.distance(first, n.strip()) for n in name_db.split(',')])])
                if len(names) > 2:
                    nli.at[ii, 'years'] = names[2]
            if distance > 0:
                issues = 'Name mismatch'
            # --- Harpaz_ID ---
            htmlp_lower = htmlp.lower()
            if 'harpaz_id' in htmlp_lower:
                harpaz_id = htmlp_lower.split('harpaz_id')[1].split('"')[2][1:]
                harpaz_id = harpaz_id[:harpaz_id.index('<')]
                if harpaz_id.isnumeric():
                    harpaz_id = int(harpaz_id)
                    if harpaz_id != nli['pid'][ii]:
                        issues = issues + '; Wrong Harpaz ID'
                else:
                    harpaz_id = np.nan
                    issues = issues + '; Harpaz ID not numeric'
            else:
                harpaz_id = np.nan
                issues = issues + '; No Harpaz ID'
            nli.at[ii, 'harpaz_id'] = harpaz_id
            # --- 1Source_ID ---
            if '1source_id' in htmlp_lower:
                source_id = htmlp_lower.split('1source_id')[1].split('"')[2][1:]
                source_id = source_id[:source_id.index('<')]
                if source_id.isnumeric():
                    source_id = int(source_id)
                    if source_id != nli['pid'][ii]:
                        issues = issues + '; Wrong 1Source ID'
                else:
                    source_id = np.nan
                    issues = issues + '; 1Source ID not numeric'
            else:
                source_id = np.nan
                issues = issues + '; No 1Source ID'
            nli.at[ii, '1source_id'] = source_id
            nli.at[ii, 'issues'] = issues
            nli.to_csv(nli_path, index=False)
browser.quit()

##
nli = pd.read_csv(nli_path, dtype={'nli_id': str, 'issues': str})
for ii in range(len(nli)):
    last = str(nli['last_nli'][ii])
    is_eng = re.search(r'[a-zA-Z]', last)
    if is_eng is not None and last != 'nan':
        nli.at[ii, 'issues'] = nli['issues'][ii].replace('Name mismatch', 'English name')
    if str(nli['issues'][ii])[0] == ';':
        nli.at[ii, 'issues'] = nli['issues'][ii].replace(';', '', 1).strip()
nli.to_csv(nli_path, index=False)
