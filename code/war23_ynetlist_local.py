'''
read the table from ynet https://www.ynet.co.il/news/category/51693
NOTE - info is from the media, not formal and not validated, use with care
'''
print('ynetlist is buggy, got to restore data/ynetlist.csv from backup')
import os
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
if local:
    import pandas as pd
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    import time
    import requests
    import numpy as np
    import re
    import json
    from glob import glob



    prev = pd.read_csv('data/ynetlist.csv')
    # dfprev = pd.read_csv('data/ynetlist.csv')
    # url = 'https://atlas.jifo.co/api/connectors/9c8936a5-bd30-4d68-9715-7280389e094c'
    # url = 'https://www.ynet.co.il/news/category/51693'
    df = pd.read_csv('~/Downloads/ynetlist.csv')
    db = pd.read_csv('data/oct7database.csv')
    for ii in range(len(df)):
        # match residence first and last name
        prev_row = (prev['מקום מגורים'] == df['מקום מגורים'][ii]) & \
            (prev['שם פרטי'] == df['שם פרטי'][ii]) & \
            (prev['שם משפחה'] == df['שם משפחה'][ii])
        if sum(prev_row) == 1:
            df.at[ii, 'pid'] = prev['pid'][prev_row].values[0]
    df.to_csv('~/Documents/debug.csv')
    for iy in np.where(df['pid'].isnull())[0]:
        indb = db['שם פרטי'].str.replace('׳',"'").str.contains(str(df['שם פרטי'][iy])) & \
            db['שם משפחה'].replace('׳',"'").str.contains(str(df['שם משפחה'][iy])) & \
            db['Residence'].str.contains(df['מקום מגורים'][iy])
        indb = np.where(indb)[0]
        if len(indb == 1):
            pid = db['pid'][indb[0]]
            print(f'found {pid}')
            if pid in df['pid'].values:
                raise ValueError(f'pid {pid} already in use')
            else:
                df.at[iy, 'pid'] = pid
                print(f'added pid {pid} to ynet')
                # added = True
    df.to_csv('~/Documents/debug.csv', index=False)
    # if added:
    #     print('found PIDs for ynetlist')
    #     df.to_csv('data/ynetlist.csv', index=False)
    # print('done ynet')
    # browser.close()

