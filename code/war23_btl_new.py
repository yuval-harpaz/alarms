"""find new btl."""
import pandas as pd
import requests
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

url = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Page/Default.aspx?ID='
##
db = pd.read_csv('data/oct7database.csv')
add = pd.read_csv('data/oct7database_additional.csv')

db[''][0]
ID = [int(id.split('.aspx?ID=')[-1]) for id in db['הנצחה'].values if (str(id) != 'nan') and ('laad' in str(id))]
ID = ID + [int(id.split('.aspx?ID=')[-1]) for id in add['הנצחה'].values if (str(id) != 'nan') and ('laad' in str(id))]
maxID = np.max(ID)
# bad = [43753]
browser = webdriver.Chrome()
for id in range(maxID+1, maxID+200):
    # if id not in ID and id not in bad:
    # r = requests.get(url+str(id))
    browser.get(url+str(id))
    time.sleep(0.1)
    html = browser.page_source
    # html = r.text
    name = html[html.index('title'):]
    name = name.replace('\n','').replace('\t','').replace('\r','').strip()
    if len(name[name.index('title>')+6:name.index('</title>')].strip()) > 0:
        name = name[6:name.index('ז  ל')-1].strip()
        print(f"{id} {name}")
        if 'במות' in html:
            bemot = html.split('במות')
            bem = [x for x in bemot if ('בן' in x[-10:]) or ('בת' in x[-10:])][0]
            htmlb = html[html.index(bem):]
            age = htmlb.index('במות')
            age = htmlb[age-10:age]
            age = age[age.index('ב'):].strip()
            gender = age.split(' ')[0]
            age = int(age.split(' ')[1])
        else:
            age = 999
            gender = ''
        mun = html.index('מונצח')
        first = html[mun-100:mun].split('>')[-1].strip()

        sec = [x for x in html.split('<section>') if 'class="details"' in x]
        span = [x[x.index('<span'):-1] for x in sec[0].split('/span')[:-1]]
        res = [x for x in span if 'התגורר' in x][0]
        res = res[res.index('>')+1:]
        res = ' '.join(res.split(' ')[1:])[1:]
        loc = [x[x.index(':')+2:] for x in span if 'אירוע:' in x][0]
        row = [id, first, name, gender, age, res, loc]
        df.loc[len(df)] = row
        print(id)
##
# df = pd.DataFrame(row, columns=['ID','first','full','gender','age','residence','location'])
# df['full'] = df['full'].str.strip()
df.to_csv('data/batal.csv', index=False)
##
df = pd.read_csv('data/batal.csv')
date = df['death_date'].values

for ii in range(len(df)):
    if np.isnan(date[ii]):
        id = df['ID'][ii]
        r = requests.get(url+str(id))
        html = r.text
        dt = html[html.index('lblDeathDate'):]
        dt = dt[dt.index(',')+1: dt.index('<')].strip()
        df.at[ii, 'death_date'] = dt
        print(id)
##

map = pd.read_csv('data/oct_7_9.csv')
for ii in range(len(df)):
    row = df['oct_7_9_id'][ii]
    if row > 0:
        df.at[ii, 'oct_7_9_loc'] = map['location'][row-1]
df.to_csv('data/batal.csv', index=False)
