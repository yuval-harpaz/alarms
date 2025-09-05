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
# fill missing IDs from db
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
nli = pd.read_csv('~/Documents/nli.csv', dtype={'nli_id': str, 'issues': str})
# got_id = np.where(db['הספריה הלאומית'].notna())[0]
for ii in range(len(db)):
    row_nli = np.where(nli['pid'] == db['pid'][ii])[0]
    if len(row_nli) == 0:
        name = db['שם פרטי'][ii].strip() + ' ' + str(db['שם נוסף'][ii]).strip() + ' ' + db['שם משפחה'][ii].strip() + ' ' + str(db['כינוי'][ii]).strip()
        name = name.replace('nan', '').replace('  ', ' ').strip()
        new_row = [db['הספריה הלאומית'][ii], db['pid'][ii], np.nan, name, np.nan, np.nan, np.nan, np.nan]
        nli.loc[len(nli)] = new_row
        row_nli = len(nli)-1
    else:
        row_nli = row_nli[0]
    if str(db['הספריה הלאומית'][ii]) != 'nan':
        id_nli = db['הספריה הלאומית'][ii]
        if str(nli['nli_id'][row_nli]) == 'nan':
            nli.at[row_nli, 'nli_id'] = id_nli
        elif str(nli['nli_id'][row_nli]) != id_nli:
            print(f'Conflict for pid {db["pid"][ii]}: prev {nli["nli_id"][row_nli]} current {id_nli}')
            nli.at[row_nli, 'nli_id'] = id_nli
            nli.at[row_nli, 'issues'] = 'ID conflict'
nli.to_csv('~/Documents/nli.csv', index=False) 
input_resp = input('shearch existing? (y/n): ')
if input_resp == 'y':
    id_to_scan = db['pid'][db['הספריה הלאומית'].notna()].values
else:
    id_to_scan = nli['pid'][nli['first_nli'].isna()].values
rows = [i for i in range(len(nli)) if nli['pid'][i] in id_to_scan]
pattern = 'item_collections'
# chrome_options = uc.ChromeOptions()
# chrome_options.add_argument("user-data-dir=/home/innereye/.config/google-chrome")  # e.g. ~/.config/google-chrome
# chrome_options.add_argument("profile-directory=Default")
browser = uc.Chrome()
# browser = webdriver.Chrome()
browser.get('https://www.nli.org.il/he')  # manually confirm not a bot
ip = input('Press Enter to continue...')
for ii in rows:  # [427] :
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
                    nli.at[ii, 'year'] = names[2]
            if distance > 0:
                issues = 'Name mismatch'
            if 'harpaz_id' in htmlp.lower():
                harpaz_id = htmlp.lower().split('harpaz_id')[1].split('"')[2][1:]
                harpaz_id = harpaz_id[:harpaz_id.index('<')]
                if harpaz_id.isnumeric():
                    
                    if int(harpaz_id) != nli['pid'][ii]:
                        issues = issues + '; Wrong Harpaz ID'
                else:
                    harpaz_id = ''
                    issues = issues + '; Harpaz ID not numeric'
            else:
                harpaz_id = ''
                issues = issues + '; No Harpaz ID'
            nli.at[ii, 'issues'] = issues
            nli.at[ii, 'harpaz_id'] = harpaz_id
            nli.to_csv('~/Documents/nli.csv', index=False)
browser.quit()

# ##
# nli = pd.read_csv('~/Documents/nli.csv', dtype={'issues': str})
# for ii in range(len(nli)):
#     # seperate first last and years if in first
#     first = str(nli['first_nli'][ii])
#     if first == 'nan':
#         nli.at[ii, 'issues'] = 'ID not found'
#     else:
#         first = first.split(',')
#         if len(first) == 3 and '2' in first[2]:
#             nli.at[ii, 'first_nli'] = first[0].strip()
#             nli.at[ii, 'last_nli'] = first[1].strip()
#             nli.at[ii, 'year'] = first[2].strip()
#         # check distance between first and name
#         if ',' not in nli['first_nli'][ii]:
#             first = nli['first_nli'][ii]
#             last = nli['last_nli'][ii]
#             name = nli['name'][ii]
#             if first in name and last in name:
#                 distance = 0
#             else:
#                 distance = max([min([Levenshtein.distance(first, n) for n in name.split(' ')]),
#                                  min([Levenshtein.distance(last, n) for n in name.split(' ')])])
#             if distance > 0:
#                 issues = 'Name mismatch'
#             else:
#                 issues = ''
#             if str(nli['harpaz_id'][ii]) == 'nan':
#                 issues = issues + '; No harpaz ID'
#             else:
#                 if nli['harpaz_id'][ii] != nli['pid'][ii]:
#                     issues = issues + '; Wrong Harpaz ID'
#             if len(issues) > 0:
#                 nli.at[ii, 'issues'] = issues
# nli.to_csv('~/Documents/nli1.csv', index=False)
