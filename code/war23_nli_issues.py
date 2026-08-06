"""Improved version of war23_nli_scrape.py. First syncs ~/Documents/nli.csv with oct7database.csv:
adds missing pids and detects NLI ID conflicts between the two sources. Then opens the NLI authority page
for each relevant pid (either all with an ID, or only those not yet scraped), extracts the name from
'item_collections', computes Levenshtein distance against the database name, and checks the Harpaz_ID
and 1Source_ID (some entries have one or both). Flags issues ('Name mismatch', 'Wrong Harpaz ID',
'Wrong 1Source ID', 'English name', etc.) and saves incrementally to ~/Documents/nli.csv.
Important, the script currently fails the robot test by cloudflair. when using my personal chrome it may pass but the script hangs
"""
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
