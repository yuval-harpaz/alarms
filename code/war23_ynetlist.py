'''
read the table from ynet https://www.ynet.co.il/news/category/51693
NOTE - info is from the media, not formal and not validated, use with care
'''
import pandas as pd
from selenium import webdriver
import requests
import os
import numpy as np

try:
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        local = True
    prev = pd.read_csv('data/ynetlist.csv')
    # dfprev = pd.read_csv('data/ynetlist.csv')
    # url = 'https://atlas.jifo.co/api/connectors/9c8936a5-bd30-4d68-9715-7280389e094c'
    # url = 'https://www.ynet.co.il/news/category/51693'
    url = "https://e.infogram.com/e7de0f19-b7b4-4a33-b23e-5037fde484d1?src=embed"
    r = requests.get(url)
    html = r.text
    # browser = webdriver.Chrome()
    # browser.get(url)
    # html = browser.page_source
    html = html.replace('&nbsp', ' ').replace('\xa0', ' ')
    data = eval(html[html.index('[[['):html.index(']]]')+3])[0]
    df = pd.DataFrame(data[1:], columns=data[0])
    # df.at[np.where(df['גיל'] == '10 חודשים')[0][0], 'גיל'] = '000'
    # val = np.zeros(len(df))
    # for ii in range(len(df)):
    #     if df['גיל'][ii] == '':
    #         val[ii] = np.nan
    #     elif df['גיל'][ii] == '10 חודשים':
    #         val[ii] = 0
    #     else:
    #         val[ii] = int(df['גיל'][ii])
    ## find new lines
    prev_str = [';'.join(x).replace('nan','').replace('.0;',';') for x in prev.values[:, :-1].astype(str)]
    df_str = [';'.join(x).replace('nan','').replace('.0;',';') for x in df.values.astype(str)]
    if prev_str == df_str:
        df = prev
    else:
        df['pid'] = np.nan
        # some changes in new ynet list
        df_str = np.array(df_str)
        prev_str = np.array(prev_str)
        for ii in range(len(df)):
            prev_row = np.where(prev_str == df_str[ii])[0]
            if len(prev_row) == 1:
                df.at[ii, 'pid'] = prev['pid'][prev_row[0]]
        print('updated ynetlist')
        df.to_csv('data/ynetlist.csv', index=False)
    db = pd.read_csv('data/oct7database.csv')
    added = False
    for iy in np.where(df['pid'].isnull())[0]:
        indb = db['שם פרטי'].str.replace('׳',"'").str.contains(str(df['שם פרטי'][iy])) & \
               db['שם משפחה'].replace('׳',"'").str.contains(str(df['שם משפחה'][iy])) & \
               db['Residence'].str.contains(df['מקום מגורים'][iy])
        indb = np.where(indb)[0]
        if len(indb == 1):
            pid = db['pid'][indb[0]]
            if pid not in df['pid'].values:
                df.at[iy, 'pid'] = pid
                print(f'added pid {pid} to ynet')
                added = True
    if added:
        print('found PIDs for ynetlist')
        df.to_csv('data/ynetlist.csv', index=False)
    print('done ynet')
    # browser.close()
except Exception as e:
    print('war23_ynetlist.py failed')
    a = os.system('echo "war23_ynetlist.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')
