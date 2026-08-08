"""find new btl."""
import pandas as pd
# import requests
import os
import numpy as np
from selenium import webdriver
import time
from datetime import datetime

local = '/home/yuval/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
# dfprev = pd.read_csv('data/ynetlist.csv')
# url = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Default.aspx?'+\
#       'lastName=&firstName=&fatherName=&motherName=&place=&year=2023&month=10&day=7&yearHeb=&monthHeb=&dayHeb=&region=&period=&grave='

url = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Page/Default.aspx?ID='
##
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
additional = pd.read_csv('data/oct7database_additional.csv')
db = [int(l.split('ID=')[1]) for l in db['הנצחה'] if 'btl' in str(l)] + [int(l.split('ID=')[1]) for l in additional['הנצחה'] if 'btl' in str(l)]
first_7oct = np.min(db)
geni = pd.read_excel('~/Documents/BTL.xlsx')
already = np.sort(np.array([int(l.split('ID=')[1]) for l in geni['לינק בטלא']]))
missing = [m for m in db if m not in already]

bad = [44144, 44172, 44200, 44210, 44251, 44270, 44271, 44272, 45638, 45639, 45655, 45657, 45662]
missing_bad = [b for b in bad if b not in already]

browser = webdriver.Chrome()
# time0 = time.time()
# for ii in range(5):
#     browser.get(url+str(ii))
# print(time.time()-time0)
# time0 = time.time()
# for ii in range(5):
#     browser.get(url+str(bad[ii]))
# print(time.time()-time0)

notyet = [k for k in np.arange(first_7oct) if k not in already]
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
fn = f"~/Documents/btl_new_{timestamp}.csv"
os.system(f'echo "ID,name" >> {fn}')
for ii in notyet:

    browser.get(url+str(ii))
    time.sleep(0.1)
    html = browser.page_source
    # html = r.text
    name = html[html.index('title'):]
    name = name.replace('\n', '').replace('\t', '').replace('\r', '').strip()
    if len(name[name.index('title>')+6:name.index('</title>')].strip()) > 0:
        name = name[6:name.index('ז  ל')-1].strip()
        print(f'{ii} {name}')
        print('')
    else:
        name = ''
    # print('test')
    # print(id, end="")
    os.system(f'echo "{ii},{name}" >> {fn}')
    print(f"{ii} / {first_7oct}", end='\r')
