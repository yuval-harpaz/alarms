import pandas as pd
import os
import numpy as np
import sys
import requests
import json
from selenium import webdriver
from time import sleep
# sys.path.append('code')
browser = webdriver.Chrome()
row = -1
for skip in range(0, 721, 20):
    url = f'https://www.gov.il/he/Departments/DynamicCollectors/is-db?skip={skip}'
    # url = 'https://www.gov.il/he/Departments/DynamicCollectors/is-db?skip=40'
    browser.get(url)
    sleep(1)
    html = browser.page_source
    segs = html.split('פריט מספר')[1:]
    while len(segs) == 0:
        sleep(1)
        html = browser.page_source
        segs = html.split('פריט מספר')[1:]
    print(f"{skip} {len(segs)}")
    if skip == 0:
        columns = []
        label = segs[0].split('<label>')[1:]
        for lbl in label:
            columns.append(lbl[:lbl.index('<')])
        df = pd.DataFrame(columns=columns)
    for seg in segs:
        row += 1
        for col in columns:
            part = seg[seg.index(col):]
            part = part[part.index(':true')+7:part.index('</span')]
            part = part.replace('<bdi>', '').replace(' 00:00:00</bdi>', '')
            df.at[row, col] = part

df.to_csv('~/Documents/prisoners.csv', index=False)
