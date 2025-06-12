"""find new btl."""
import pandas as pd
# import requests
import os
import numpy as np
from selenium import webdriver
import time

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
# dfprev = pd.read_csv('data/ynetlist.csv')
# url = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Default.aspx?'+\
#       'lastName=&firstName=&fatherName=&motherName=&place=&year=2023&month=10&day=7&yearHeb=&monthHeb=&dayHeb=&region=&period=&grave='

url = 'https://www.nli.org.il/he/search?projectName=NLI#&q=any,contains,FIRST%20LAST&bulkSize=30&index=0&sort=rank&t=authorities&mode=basic'
#
# db = pd.read_csv('data/oct7database.csv')

# nli = pd.DataFrame(columns=['pid', 'first', 'last', 'nli_id', 'harpaz_id', 'candidates'])
# nli['pid'] = pid
# nli['first'] = first
# nli['last'] = last
# nli['nli_id'] = np.nan
# nli['harpaz_id'] = np.nan
nli = pd.read_csv('data/nli.csv')
for ii in range(len(nli)):
    if nli['nli_id'].isna().values[ii]:
        nli.at[ii, 'nli_id'] = ''
    else:
        nli.at[ii, 'nli_id'] = str(int(nli['nli_id'].values[ii]))
first = nli['first'].values
last = nli['last'].values
pid = nli['pid'].values
not_yet = range(np.where(~nli['candidates'].isna())[0][-1], len(first))
marker = 'authorities/'
browser = webdriver.Chrome()
browser.get('https://www.nli.org.il/he')
ip = input('Press Enter to continue...')
for ii in not_yet:  #  range(len(first)):  # [427]
    browser.get(url.replace('FIRST', first[ii]).replace('LAST', last[ii]))
    time.sleep(0.5)
    html = browser.page_source
    nli_id = None
    harpaz_id = None
    candidates = []
    if 'אישיות' in html:
        print('Found אישיות for', first[ii], last[ii])
        segments = html.split('אישיות')
        if len(segments) > 1:
            for segment in segments[1:]:
                if marker in segment:
                    idx = segment.index(marker)
                    candidates.append(segment[idx+len(marker):idx+len(marker)+18])
        candidates = np.unique(candidates)
        
        if len(candidates) > 0:
            for candidate in candidates:
                personal = 'https://www.nli.org.il/he/authorities/'+candidate
                browser.get(personal)
                htmlp = browser.page_source
                if first[ii] in htmlp and last[ii] in htmlp:
                    idxp = htmlp.index(last[ii])
                    name = htmlp[idxp:].split('<')[0].strip()
                    if first[ii] and last[ii] in name:
                        nli_id = candidate
                        if 'Harpaz_ID' in htmlp:
                            harpaz_id = htmlp.split('Harpaz_ID')[1].split('"')[2][1:]
                            harpaz_id = harpaz_id[:harpaz_id.index('<')]
                        break
    if len(candidates) == 0:
        cand = None
    else:
        cand = str(candidates)[2:-2].replace("' '", ';')
        nli.at[ii, 'nli_id'] = nli_id
        nli.at[ii, 'harpaz_id'] = harpaz_id
        nli.at[ii, 'candidates'] = cand
        nli.to_csv('data/nli.csv', index=False)
browser.quit()