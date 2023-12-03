import pandas as pd
import requests
import os

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
try:
    # dfprev = pd.read_csv('data/ynetlist.csv')
    url = 'https://www.haaretz.co.il/news/2023-11-23/ty-article-magazine/0000018b-4196-d242-abef-53b654760000'
    r = requests.get(url)
    html = r.text
    segs = html.split('war-kidnapped-card filterd')
    segs = segs[1:]

    ##
    condition = 'חטוף'
    data = []
    for iseg in range(len(segs)):
        seg = segs[iseg]
        comp = seg.split('|')
        if '">' not in comp[3]:
            break
        status = seg[seg.index('data-sort')+11]
        name_age = comp[0][comp[0].index('data-filter')+13:]
        name = name_age.split(',')[0].strip()
        if ',' in name_age:
            age = name_age.split(',')[1].strip()
        else:
            age = ''
        fro = comp[1].strip()
        # comp2 = comp[2].strip()
        story = comp[3][:comp[3].index('">')].strip()
        data.append([name, age, fro, status, condition, story])
        if 'החטופים שהוחזרו עד כה' in seg:
            condition = 'שוחרר'
        elif 'חטופים שגופתם' in seg:
            condition = 'הוחזר'
        elif 'ישראלים נוספים' in seg:
            condition = 'נוספים'
    df = pd.DataFrame(data, columns=['name', 'age', 'from', 'status', 'condition', 'story'])
    df['story'] = df['story'].str.replace('<br>', '\n')
    df['story'] = df['story'].str.strip()
    status_replace = [['c', 'אזרח'], ['s', 'חייל'], ['-', '']]
    stat = df['status'].values
    for istat in range(len(status_replace)):
        stat[stat == status_replace[istat][0]] = status_replace[istat][1]
    df['status'] = stat
    df.to_csv('data/kidnapped_haaretz.csv', index=False)

    ##
except Exception as e:
    print('war23_haaretz_kidnapped.py failed')
    a = os.system('echo "war23_haaretz_kidnapped.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')
