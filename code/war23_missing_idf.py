import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True
csv = 'data/tmp_deaths_idf.csv'
# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:
with Display() as disp:
    try:
        browser = webdriver.Chrome()
    except:
        print('no chrome? trying firefox')
        browser = webdriver.Firefox()
    already = 0
    data = []
    goon = True
    page = 0
    while goon:
        page += 1
        prev = len(data)
        url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
        browser.get(url)
        time.sleep(0.1)
        html = browser.page_source
        if page == 1:
            itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
            tot = html[itot-10:itot+10]
            tot = tot[tot.index('>')+1:]
            tot = int(tot[:tot.index(' ')])
        segs = html.split('ol-lg-6 col-md-6 wrap-item')
        for iseg in range(1, len(segs)):
            if goon:
                seg = segs[iseg]
                personal = seg[seg.index('href=')+5:seg.index('aria-')]
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
                print(name)
                data.append(name)
        if len(data) == prev:  # new page with no names
            goon = False
        else:
            print(len(data))
    browser.close()
    # return data, tot
    df = pd.DataFrame(data, columns=['name'])
    df = df.iloc[::-1]
    # df = pd.concat([dfprev, df], ignore_index=True)
    # df = df.sort(['death_date', 'name'], ascending=[False, True])
    df.to_csv('tmp_name.csv', index=False)
    # df = df.sort_values('death_date', ignore_index=True)
    # df.drop_duplicates('name', inplace=True, ignore_index=True)


