import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np
import re
local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True

df = pd.read_csv('data/idf_dashboard.csv')
# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:
keys = ['מתחילת המלחמה','מתחילת התמרון','מצב מאושפזים נוכחי','פצועים מתחילת המלחמה','פצועים מתחילת התמרון ברצועת עזה']
conds = ['קל','בינוני','קשה']
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:10].replace('T', ' ')
try:
    with Display() as disp:
        try:
            browser = webdriver.Chrome()
        except:
            print('no chrome? trying firefox')
            browser = webdriver.Firefox()
        url = 'https://www.idf.il/160590'
        browser.get(url)
        time.sleep(0.1)
        html = browser.page_source
        idate = re.search('\d{2}\.\d{2}\.\d{2}', html).start()
        date = html[idate:idate+8]
        date = '20'+'-'.join(date.split('.')[::-1])
        # if date in df['תאריך'].values:
        #     print(date+' already in idf_dashboard.csv')
        # else:
        data = [nowstr]
        for ii in range(len(keys)):
            idx = html.index(keys[ii])
            segment = html[idx:idx+2000]
            if ii < 2:
                segment = segment[segment.index('counters'):]
                val = segment.split('\n')[1].strip()
                data.append(val)
                if not val.isnumeric():
                    raise Exception('expected numeric for '+keys[ii])
            else:
                for icond in range(len(conds)):
                    cond = conds[icond]
                    seg = segment[segment.index(cond):]
                    seg = seg[seg.index('counters'):]
                    val = seg.split('\n')[1].strip()
                    data.append(val)
                    if not val.isnumeric():
                        raise Exception('expected numeric for ' + keys[ii]+' '+cond)
        browser.close()
        if data[0] == df['תאריך'].values[-1]:
            print(f'idf dashboard date {nowstr} exists')
            print(str(data))
            print('not saving')
        else:
            if list(df.iloc[-1].values[1:]) == data[1:]:
                print('data is the same as last row')
            df.loc[len(df)] = data
            df.to_csv('data/idf_dashboard.csv', index=False)
            df.to_excel('data/idf_dashboard.xlsx', index=False, sheet_name='Sheet1')
            print(f'added a line to idf_dashboard.csv')

except Exception as e:
    print('war23_idf_dashboard.py failed')
    a = os.system('echo "war23_idf_dashboard.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')


#
# columns = ['מתחילת המלחמה','מתחילת התמרון',
#            'מצב מאושפזים נוכחי קל', 'מצב מאושפזים נוכחי בינוני', 'מצב מאושפזים נוכחי קשה',
#            'פצועים מתחילת המלחמה קל', 'פצועים מתחילת המלחמה בינוני', 'פצועים מתחילת המלחמה קשה',
#            'פצועים ברצועת עזה קל', 'פצועים ברצועת עזה בינוני', 'פצועים ברצועת עזה קשה']
#
# df.columns = columns
