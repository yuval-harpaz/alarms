import requests
import pandas as pd
from html import unescape
import os
import sys
import re
import numpy as np
try:
    local = '/home/innereye/alarms/'
    islocal = False
    if os.path.isdir(local):
        os.chdir(local)
        islocal = True
        sys.path.append(local + 'code')
except Exception as e:
    print('set path failed?')
    print(e)

from map_deaths import map_deaths
replace = [['כדורגלן עבר', ''],
           ['ממבטחים', 'מבטחים'],
           ['מבטחים', 'ממבטחים']]

try:
    r = requests.get('https://ynet-projects.webflow.io/news/attackingaza?01ccf7e0_page=100000000')
    bad = len(r.text)
    # marker seperates between people
    marker = '<div class="fallen-text-top w-condition-invisible">'
    gpa = 'gazaattack-place-age'
    gns = 'gazaattack-name-story'
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
            idx_marker = [m.end() for m in re.finditer(marker, txt)]
            # segment = txt.split('r-field="name" class="gazaattack-name"')
            ##
            gender = ['']*len(idx_marker)
            age = np.zeros(len(idx_marker), int)
            loc = ['']*len(idx_marker)
            story = ['']*len(idx_marker)
            name = ['']*len(idx_marker)
            # seg_count = -1
            for iseg in range(len(idx_marker)):  # segment[1:]:
                # age.append(0)
                seg = txt[idx_marker[iseg]+len('<div fs-cmsfilter-field="name" class="gazaattack-name">'):]
                if iseg < len(idx_marker)-2:
                    seg = seg[:(idx_marker[iseg+1]-idx_marker[iseg])]
                name[iseg] = seg[:seg.index('<')]
                if 'טל לוי' in seg[:8]:
                    # loc[iseg] = '')
                    # gender[iseg] = '')
                    # age.append(0)
                    story[iseg] = 'מ"כ בגדוד 50'
                    # print('booha')
                else:
                    segs = seg.split('<div fs-cmsfilter-field="age" class="gazaattack-place-age">')
                    for s in segs:
                        a = s.replace('</div>', '')
                        if a.isnumeric():
                            age[iseg] = int(a)
                            break
                    segs = seg.split('<div fs-cmsfilter-field="age" class="gazaattack-place-age">')
                    for s in segs:
                        if '<div class="redlinegazaattack"></div>' in s:
                            l = s[:s.index('<')]
                            if l.replace(' ', '').isalpha() and not l == name[iseg]:
                                loc[iseg] = l
                                break
                if age[iseg] == '':
                    if gpa in seg:
                        idx = seg.index(gpa)
                        segan = seg[idx + len(gpa) + 1:]
                        segan = segan[:segan.index('<')]
                        if '>בת' in segan:
                            gender[iseg] = 'F'
                            gindex = segan.index('>בת')+1
                        elif '>בן' in segan:
                            gender[iseg] = 'M'
                            gindex = segan.index('>בן')+1
                        else:
                            # gender[iseg] = '')
                            gindex = None
                        if gindex is None:
                            # print('no age for ' + name[-1])
                            # age.append(0)
                            segan_split = segan.split(' ')
                            im = []
                            for ii in range(len(segan_split)):
                                if segan_split[ii].replace('>', '')[0] == 'מ':
                                    im.append(ii)
                            if len(im) == 0:
                                lc = segan.replace('>', '')
                                lc = lc.replace('w-dyn-bind-empty"', '')
                                loc[iseg] = lc
                            else:
                                lc = ' '.join(segan_split[im[-1]:]).replace('>', '')
                                lc = lc.replace('-dyn-bind-empty">', '')
                                loc[iseg] = lc
                        else:
                            ag = segan[gindex+3:]
                            if ag[0].isnumeric():
                                for ichar in range(1, len(ag)):
                                    if ag[ichar].isnumeric():
                                        a = int(ag[:ichar+1])
                                    else:
                                        break
                                age[iseg] = a
                                if ichar != len(ag)-1:
                                    # loc[iseg] = '')
                                # else:
                                    loc[iseg] = ag[ichar:].replace(',', '').strip()
                                if len(loc[-1]) > 0 and loc[-1][0] == 'מ':
                                    loc[iseg] = loc[-1][1:]
                            else:
                                # raise Exception('no age here?')
                                # age.append(0)
                                loc[iseg] = '?'
                    if gns in seg:
                        seg = seg[seg.index(gns):]
                        story[iseg] = seg[len(gns)+2:seg.index('<')].replace('-dyn-bind-empty">', '')
                    # else:
                        # story[iseg] = '')
            df = pd.DataFrame(name, columns=['name'])
            df['gender'] = gender
            df['age'] = age
            df['from'] = loc
            df['story'] = story
            dfs.append(df)
    merged = pd.concat(dfs)
    merged.to_excel('data/deaths.xlsx', index=False)
    merged.to_csv('data/deaths.csv', index=False)
    success = True
except Exception as e:
    print('scraping ynet failed')
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
    success = False
# age0 = txt.index('gazaattack-place-age')
if success:
    try:
        map_deaths()
    except Exception as e:
        print('death map creation failed')
        print(e)
print('done')
