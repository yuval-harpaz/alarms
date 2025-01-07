import pandas as pd
import requests
import os
try:
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        local = True
    url = 'https://www.haaretz.co.il/news/2023-10-12/ty-article-magazine/0000018b-1367-dcc2-a99b-17779a0a0000'
    r = requests.get(url)
    html = r.text
    html = html.replace('u003e', '>')
    segs = html.split('war-victims-card filterd')
    segs = segs[1:]

    ##
    # condition = 'חטוף'
    data = []
    for iseg in range(len(segs)):
        seg = segs[iseg].replace('\\', '')
        comp = seg.split('|')
        if '">' not in comp[3]:
            break

        status = seg[seg.index('data-sort')+11]
        name_age = comp[0][comp[0].index('data-filter')+13:]
        name = name_age.split(',')[0].strip()
        if len(name) > 0:
            if ',' in name_age:
                age = name_age.split(',')[1].strip()
            else:
                age = ''
            fro = comp[1].strip()
            # comp2 = comp[2].strip()
            story = comp[3][:comp[3].index('">')].strip()
            data.append([name, age, fro, status, story])
    df = pd.DataFrame(data, columns=['name', 'age', 'from', 'status', 'story'])
    df['story'] = df['story'].str.replace('<br>', '\n')
    df['story'] = df['story'].str.strip()
    status_replace = [['c', 'אזרח'],['s','חייל'],['p','שוטר'],['r','הצלה']]
    stat = df['status'].values
    for istat in range(4):
        stat[stat == status_replace[istat][0]] = status_replace[istat][1]
    df['status'] = stat
    if len(df) < 1000:
        print('war23_haaretz_deaths.py failed')
        a = os.system('echo "war23_haaretz_deaths.py empty list" >> code/errors.log')
    else:
        df.to_csv('data/deaths_haaretz.csv', index=False)
except Exception as e:
    print('war23_haaretz_deaths.py failed')
    a = os.system('echo "war23_haaretz_deaths.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')
