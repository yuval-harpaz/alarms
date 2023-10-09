import requests
import pandas as pd
from html import unescape
r = requests.get('https://ynet-projects.webflow.io/news/attackingaza')
r.encoding = r.apparent_encoding
txt = r.text
txt = unescape(txt)
segment = txt.split('r-field="name" class="gazaattack-name"')
##
gender = []
age = []
loc = []
story = []
name = []
for seg in segment[1:]:
    name.append(seg[1:seg.index('<')])
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
# df.to_excel('/home/innereye/alarms/data/deaths.xlsx', index=False)
df.to_csv('data/deaths.csv', index=False)
# age0 = txt.index('gazaattack-place-age')


