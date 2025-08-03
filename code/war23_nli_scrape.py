"""find new btl."""
import pandas as pd
# import requests
import os
import numpy as np
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import re
import Levenshtein



local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
# url = 'https://www.nli.org.il/he/search?projectName=NLI#&q=any,contains,FIRST%20LAST&bulkSize=30&index=0&sort=rank&multiFacets=facet_local18,include,2023,1|,|facet_local18,include,2024,1|,|facet_local18,include,2025,1&t=authorities'

db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})

nli = pd.DataFrame(columns=['pid', 'harpaz_id', 'name', 'first_nli', 'last_nli', 'issues'])
nli['pid'] = db['pid'].values
nli['name'] = db['שם פרטי'].str.strip() + ' ' + db['שם נוסף'].astype(str).str.strip() + ' ' + db['שם משפחה'].str.strip() + ' ' + db['כינוי'].astype(str).str.strip()
nli['name'] = nli['name'].str.replace('nan', '').replace('  ', ' ').str.strip()
# nli['harpaz_id'] = ''
# browser = webdriver.Chrome()
chrome_options = uc.ChromeOptions()
# chrome_options = Options()
chrome_options.add_argument("user-data-dir=/home/innereye/.config/google-chrome")  # e.g. ~/.config/google-chrome
chrome_options.add_argument("profile-directory=Default")
# chrome_options.add_argument("--remote-allow-origins=*")

# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option('useAutomationExtension', False)
# browser = uc.Chrome(options=chrome_options)
# browser = webdriver.Chrome(options=chrome_options)
# Execute script to hide webdriver property
# browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
browser = uc.Chrome()
browser.get('https://www.nli.org.il/he')
# personal = 'https://www.nli.org.il/he/authorities/'+db['הספריה הלאומית'][0]
# browser.get(personal)

ip = input('Press Enter to continue...')
got_id = np.where(db['הספריה הלאומית'].notna())[0]
pattern = 'item_collections'
for ii in got_id:  # [427] :
    personal = 'https://www.nli.org.il/he/authorities/'+db['הספריה הלאומית'][ii]
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
        if len(names) == 2:
            nli.at[ii, 'first_nli'] = names[0]
            nli.at[ii, 'last_nli'] = names[1]
        else:
            nli.at[ii, 'first_nli'] = name
            nli.at[ii, 'last_nli'] = ''
        if 'harpaz_id' in htmlp.lower():
            harpaz_id = htmlp.lower().split('harpaz_id')[1].split('"')[2][1:]
            harpaz_id = harpaz_id[:harpaz_id.index('<')]
        else:
            harpaz_id = ''
        nli.at[ii, 'harpaz_id'] = harpaz_id
        nli.to_csv('~/Documents/nli.csv', index=False)
browser.quit()

##
nli = pd.read_csv('~/Documents/nli.csv', dtype={'issues': str})
for ii in range(len(nli)):
    # seperate first last and years if in first
    first = str(nli['first_nli'][ii])
    if first == 'nan':
        nli.at[ii, 'issues'] = 'ID not found'
    else:
        first = first.split(',')
        if len(first) == 3 and '2' in first[2]:
            nli.at[ii, 'first_nli'] = first[0].strip()
            nli.at[ii, 'last_nli'] = first[1].strip()
            nli.at[ii, 'year'] = first[2].strip()
        # check distance between first and name
        if ',' not in nli['first_nli'][ii]:
            first = nli['first_nli'][ii]
            last = nli['last_nli'][ii]
            name = nli['name'][ii]
            if first in name and last in name:
                distance = 0
            else:
                distance = max([min([Levenshtein.distance(first, n) for n in name.split(' ')]),
                                 min([Levenshtein.distance(last, n) for n in name.split(' ')])])
            if distance > 0:
                issues = 'Name mismatch'
            else:
                issues = ''
            if str(nli['harpaz_id'][ii]) == 'nan':
                issues = issues + '; No harpaz ID'
            else:
                if nli['harpaz_id'][ii] != nli['pid'][ii]:
                    issues = issues + '; Wrong Harpaz ID'
            if len(issues) > 0:
                nli.at[ii, 'issues'] = issues
nli.to_csv('~/Documents/nli1.csv', index=False)
