import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np

local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True
##
df = pd.read_csv('data/oct7database.csv')
idf = pd.read_csv('data/deaths_idf.csv')
nopid = np.where(idf['pid'].isnull())[0]
if len(nopid) > 0:
    browser = webdriver.Firefox()
    for ii in range(len(nopid)):
        name = idf['name'][nopid[ii]]
        ns = name.split(' ')
        pid = df['pid'].max()+1
        irow = len(df)
        row = [np.nan]*df.shape[1]
        row[0] = pid
        row[5] = ns[0]
        row[6] = ns[-1]
        if len(ns) > 2:
            row[7] = ' '.join(ns[1:-1])
        url = 'https://www.idf.il/' + 'נופלים/חללי-המלחמה/' + '-'.join(name.split(' '))
        browser.get(url)
        time.sleep(0.1)
        htmlp = browser.page_source
        if 'אין מה לראות כאן' in htmlp:
            urls.append('')
            eng.append('')
        else:
            urls.append(urlp)
            if 'z"l' in htmlp:
                htmlp = htmlp[htmlp.index("small"):]
                htmlp = htmlp[:htmlp.index('z"l')]
                en = htmlp[::-1]
                en = en[:en.index('>')][::-1].strip()
                if '(res.)' in en:
                    en = en[en.index('(res.)') + 6:].strip()
                elif 'class' in en.lower():
                    en = en[en.lower().index('class') + 5:].strip()
                else:
                    rank = [x for x in ['sergeant', 'sergent', 'captain', 'lieutenant', 'major'] if x in en.lower()]
                    if len(rank) == 1:
                        en = en[en.lower().index(rank[0]) + len(rank[0]):].strip()
                en = en.split(' ')
            else:
                eng.append('')




# data = data[~data['issues'].isnull()]
data.to_csv('/home/innereye/Documents/issues_url.csv', index = False)
##
for ii in range(954, len(data)):
    url = data['הנצחה'][ii]
    if '.btl.' not in url:
        browser.get(url)
        time.sleep(0.1)
        html = browser.page_source
        if '.idf.' in url:
            columns = colall
        else:
            columns = colheb
        issue = ''
        for col in columns:
            nm = data[col][ii]
            if str(nm) != 'nan':
                if nm not in html:
                    issue = issue + ' ' + nm
        if issue == '':
            issue = np.nan
        else:
            issue = issue.strip()
        data.at[ii, 'issues'] = issue
    else:
        data.at[ii, 'issues'] = np.nan

##
data = pd.read_csv('/home/innereye/Documents/issues_url.csv')
colall = list(data.columns[1:9])
colheb = list(data.columns[5:9])
browser = webdriver.Firefox()
for ii in range(760, len(data)):
    url = data['הנצחה'][ii]
    if '.btl.' in url:
        time.sleep(1.05)
        browser.get(url)
        time.sleep(0.1)
        html = browser.page_source
        if '.idf.' in url:
            columns = colall
        else:
            columns = colheb
        issue = ''
        for col in columns:
            nm = data[col][ii]
            if str(nm) != 'nan':
                if nm not in html:
                    issue = issue + ' ' + nm
        if issue == '':
            issue = np.nan
        else:
            issue = issue.strip()
        data.at[ii, 'issues'] = issue
    # else:
        # data.at[ii, 'issues'] = np.nan
#
data.to_csv('/home/innereye/Documents/issues_url.csv', index = False)
data = data[~data['issues'].isnull()]
data.to_csv('/home/innereye/Documents/issues_url_gist.csv', index = False)