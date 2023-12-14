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
csv = 'data/deaths_idf.csv'
only_new = False
# if only_new:
dfprev = pd.read_csv('data/deaths_idf.csv')
#     id = []
#     for x in range(len(dfprev)):
#         id.append('|'.join([dfprev['name'][x], str(dfprev['age'][x]), str(dfprev['from'][x]).replace('nan','')]))
#     id = np.array(id)

# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:


browser = webdriver.Firefox()
already = 0
data = []
goon = True
page = 0
name = []
for page in range(1, 46):
    prev = len(data)
    url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
    browser.get(url)
    time.sleep(0.1)
    html = browser.page_source
    # if page == 1:
    #     itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
    #     tot = html[itot-10:itot+10]
    #     tot = tot[tot.index('>')+1:]
    #     tot = int(tot[:tot.index(' ')])
    segs = html.split('ol-lg-6 col-md-6 wrap-item')
    for iseg in range(1, len(segs)):
        if goon:
            seg = segs[iseg]
            personal = seg[seg.index('href=')+5:]  # no more seg.index('aria-')
            personal = personal[personal.index('"')+1:]
            personal = personal[:personal.index('"')]
            seg = seg[seg.index('solder-name'):]
            if '2023)' in seg:
                iyear = segs[iseg].index('2023)')
                date = segs[iseg][iyear - 6:iyear + 4]
                date = '-'.join(date.split('.')[::-1])
            else:
                date=''
            # seg = segs[iseg][:iyear+5]
            rank = seg[seg.index("small")+7:]
            rank = rank[:rank.index('<')]
            name = seg.split('\n')[2].strip()
            if dfprev.iloc[len(dfprev)-len(data)-1]['name'] != name:
                print(name)
                # raise Exception('unexpexted')
            data.append(name)
data = data[::-1]
df = pd.DataFrame(data, columns=['name'])

# df = pd.DataFrame(data, columns=['death_date', 'name', 'rank', 'unit', 'gender', 'age', 'from','story'])
df.to_csv('data/tmp.csv', index=False)
