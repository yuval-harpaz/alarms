'''
read the table from ynet https://www.ynet.co.il/news/category/51693
NOTE - info is from the media, not formal and not validated, use with care
'''
import pandas as pd
# from selenium import webdriver
import requests
import os
try:
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        local = True
    # dfprev = pd.read_csv('data/ynetlist.csv')
    url = 'https://atlas.jifo.co/api/connectors/9c8936a5-bd30-4d68-9715-7280389e094c'
    r = requests.get(url)
    html = r.text
    # browser = webdriver.Chrome()
    # browser.get(url)
    # html = browser.page_source
    html = html.replace('&nbsp', ' ')
    data = eval(html[html.index('[[['):html.index(']]]')+3])[0]
    df = pd.DataFrame(data[1:], columns=data[0])
    df.to_csv('data/ynetlist.csv', index=False)
    # browser.close()
except Exception as e:
    print('read ynet failed')
    print(e)
