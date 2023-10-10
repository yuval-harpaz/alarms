import requests
import pandas as pd
from html import unescape
import os

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

replace = [['כדורגלן עבר', ''],
           ['ממבטחים', 'מבטחים'],
           ['מבטחים', 'ממבטחים']]

r = requests.get('https://ynet-projects.webflow.io/news/attackingaza?01ccf7e0_page=100000000')
bad = len(r.text)
dfs = []
page = 0
more = True
while more:
    page += 1
    # r = requests.get('https://ynet-projects.webflow.io/news/attackingaza')
    r = requests.get(f'https://ynet-projects.webflow.io/news/attackingaza?01ccf7e0_page={page}')
    if len(r.text) == bad or page > 100:
        more = False
    else:
        r.encoding = r.apparent_encoding,
        txt = r.text
        txt = unescape(txt)
        for rep in replace:
            txt = txt.replace(rep[0], rep[1])
        segment = txt.split('r-field="name" class="gazaattack-name"')
        ##
        gender = []
        age = []
        loc = []
        story = []
        name = []
        for seg in segment[1:]:
            name.append(seg[1:seg.index('<')])
            if 'טל לוי' in seg:
                loc.append('')
                gender.append('')
                age.append(0)
                story.append('מ"כ בגדוד 50')
                print('booha')
            else:
                idx = seg.index('gazaattack-place-age')
                segan = seg[idx + len('gazaattack-place-age') + 1:]
                segan = segan[:segan.index('<')]
                if '>בת' in segan:
                    gender.append('F')
                    gindex = segan.index('>בת')+1
                elif '>בן' in segan:
                    gender.append('M')
                    gindex = segan.index('>בן')+1
                else:
                    gender.append('')
                    gindex = None
                if gindex is None:
                    print('no age for ' + name[-1])
                    age.append(0)

                    segan_split = segan.split(' ')
                    im = []
                    for ii in range(len(segan_split)):
                        if segan_split[ii].replace('>', '')[0] == 'מ':
                            im.append(ii)
                    if len(im) == 0:
                        lc = segan.replace('>', '')
                        lc = lc.replace('w-dyn-bind-empty"', '')
                        loc.append(lc)
                    else:
                        lc = ' '.join(segan_split[im[-1]:]).replace('>', '')
                        lc = lc.replace('-dyn-bind-empty">', '')
                        loc.append(lc)
                    # loc.append('')

                else:
                    ag = segan[gindex+3:]
                    if ag[0].isnumeric():
                        for ichar in range(1, len(ag)):
                            if ag[ichar].isnumeric():
                                a = int(ag[:ichar+1])
                            else:
                                break
                        age.append(a)
                        if ichar == len(ag)-1:
                            loc.append('')
                        else:
                            loc.append(ag[ichar:].replace(',', '').strip())
                        if len(loc[-1]) > 0 and loc[-1][0] == 'מ':
                            loc[-1] = loc[-1][1:]
                    else:
                        # raise Exception('no age here?')
                        # age.append(0)
                        loc.append('?')
                seg = seg[seg.index('gazaattack-name-story'):]
                story.append(seg[len('gazaattack-name-story')+2:seg.index('<')].replace('-dyn-bind-empty">', ''))
        df = pd.DataFrame(name, columns=['name'])
        df['gender'] = gender
        df['age'] = age
        df['from'] = loc
        df['story'] = story
        dfs.append(df)
merged = pd.concat(dfs)
merged.to_excel('data/deaths.xlsx', index=False)
merged.to_csv('data/deaths.csv', index=False)
# age0 = txt.index('gazaattack-place-age')


