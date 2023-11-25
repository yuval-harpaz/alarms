import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from selenium import webdriver
from datetime import datetime
import os
from pyvirtualdisplay import Display
local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
dfprev = pd.read_csv('data/war23_idf_deaths.csv')
##
def get_deaths():

    browser = webdriver.Chrome()
    already = 0
    data = []
    goon = True
    page = 0
    while goon:
        page += 1
        prev = len(data)
        url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
        browser.get(url)
        html = browser.page_source
        if page == 1:
            itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
            tot = html[itot-10:itot+10]
            tot = tot[tot.index('>')+1:]
            tot = int(tot[:tot.index(' ')])
        segs = html.split('solder-name')
        for iseg in range(1, len(segs)):
            if goon:
                seg = segs[iseg]
                if '2023)' in seg:
                    iyear = segs[iseg].index('2023)')
                    date = seg[iyear - 6:iyear + 4]
                    date = '-'.join(date.split('.')[::-1])
                else:
                    date=''
                # seg = segs[iseg][:iyear+5]
                rank = seg[seg.index("small")+7:]
                rank = rank[:rank.index('<')]
                name = seg.split('\n')[2].strip()
                if name in dfprev['name'].values:
                    already += 1
                    print('already ' + name)
                    if already == 2:
                        goon = False
            if goon:
                unit = seg.split('\n')[6].strip()
                urlp = 'https://www.idf.il/נופלים/חללי-המלחמה/'+'-'.join(name.split(' '))
                for rep in ["'"]:
                    urlp = urlp.replace(rep, '-')
                for rep in ["(", ")"]:
                    urlp = urlp.replace(rep, '')
                browser.get(urlp)
                htmlp = browser.page_source
                if 'בנופ' not in htmlp:
                    fro = ''
                    age = 0
                    story = ''
                    gender = ''
                    if 'נפטר' in htmlp:
                        fro = htmlp.split(',')[3][2:]
                        ifro = htmlp.index(fro)
                        story = htmlp[ifro + len(fro) + 2:]
                        story = story[:story.index('\n')]
                    else:
                        print('failed for ' + urlp.split('/')[-1])
                else:
                    fro = htmlp.split(',')[3][2:]
                    ifro = htmlp.index(fro)
                    ifell = htmlp.index('בנופל')
                    age = int(htmlp[ifell-3:ifell-1])
                    story = htmlp[ifro+len(fro)+2:ifell-8]
                    gender = htmlp[ifell-6:ifell-4].replace('בן','M').replace('בת', 'F')
                data.append([date, name, rank, unit, gender, age, fro, story])
            if already and goon:
                data = data[:-1]
        if len(data) == prev:  # new page with no names
            goon = False
        else:
            print(len(data))
    return data, tot
##
if local:
    data, tot = get_deaths()
else:
    with Display() as disp:
        data, tot = get_deaths()
##
if len(data) > 0:
    df = pd.DataFrame(data, columns=['death_date', 'name', 'rank', 'unit', 'gender', 'age', 'from','story'])
    df = pd.concat([dfprev, df], ignore_index=True)
    df = df.sort_values('death_date', ignore_index=True)
    # df.drop_duplicates('name', inplace=True, ignore_index=True)
    if len(df) == tot:
        df.to_csv('data/war23_idf_deaths.csv', index=False)
    else:
        print(f'total should be {tot}, instead {len(df)}')
##
if local:
    df = pd.read_csv('data/war23_idf_deaths.csv')

    dates = pd.date_range(start='2023-10-07', end=datetime.today().strftime('%Y-%m-%d'), freq='D')
    df['time'] = pd.to_datetime(df['death_date'])
    # dateu = np.unique(df['time'].values)
    count = []
    for idate in range(len(dates)):
        count.append([np.sum((df['time'].values == dates[idate]) & (df['gender'] == 'M')),
                      np.sum((df['time'].values == dates[idate]) & (df['gender'] == 'F'))])
    count = np.array(count)

    ##
    lim = [300, 30]
    plt.figure()
    for sp in [1, 2]:
        plt.subplot(2,1,sp)
        plt.bar(dates, np.sum(count, 1), color='r', label='Female')
        plt.ylim(0, lim[sp-1])
        plt.bar(dates, count[:,0], color='b', label='Male')
        # ax = plt.gca()
        # ax.yaxis.grid()
        plt.grid()
        # plt.xticks(rotation=30)
        if sp == 1:
            plt.text(dates[1], 256, f'{38}/{278}')
            plt.title('מספר הנופלים לפי תאריך ומגדר'[::-1])
            plt.legend()
        else:
            plt.text(dates[5], 2, f'{1}/{1}')
            plt.text(dates[7], 3, f'{1}/{2}')
    plt.show()

