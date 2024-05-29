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
urls = []
eng = []
goon = True
page = 0
for page in range(1, 100):
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
            urlp = 'https://www.idf.il' + personal
            for rep in ["'"]:
                urlp = urlp.replace(rep, '-')
            for rep in ["(", ")"]:
                urlp = urlp.replace(rep, '')
            browser.get(urlp)
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
                    eng.append(en)
                else:
                    eng.append('')
df = pd.DataFrame(eng, columns=['name'])
df['url'] = urls
df = df[::-1]
df.to_csv('data/tmp_idf_eng.csv', index=False)
