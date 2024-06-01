import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np
from datetime import datetime
browser = webdriver.Firefox()
url = 'https://www.gov.il/en/collectors/memorialization?officeId=6cbf57de-3976-484a-8666-995ca17899ec&limit=100&memorializationType=c9fe0851-5115-41b3-9efc-d45a94ace75d'
browser.get(url)
html = browser.page_source
segs = html.split('mb-3')
df = pd.DataFrame(columns=['date','name','story','link'])
for ii in range(1, len(segs)):
    seg = segs[ii]
    link = 'https://www.gov.il'+seg[seg.index('href')+6:]
    link = link[:link.index('"')]
    name = seg[seg.index('mb-1"')+6:].strip()
    name = name[:name.index('<')]
    story = seg[seg.index('mb-1 fs-5')+11:]
    story = story[:story.index('<')]
    date = seg[seg.index('Data_1_0')+10:]
    date = date[:date.index('<')]
    # date = story[:story.index('-')-1].strip()
    date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
    df.loc[len(df)] = [date, name, story, link]

df = df[df['date'] > '2023-10-07']
df = df.sort_values('date', ignore_index=True)
df.to_csv('data/war23_mfa.csv', index=False)
##
