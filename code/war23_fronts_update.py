# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# from datetime import datetime
import Levenshtein
import re
import os
# import re
local = '/home/innereye/alarms/'
# islocal = False
try:
    if os.path.isdir(local):
        os.chdir(local)
        local = True
    csv = 'data/deaths_idf.csv'
    idf = pd.read_csv(csv)
    front = pd.read_csv('data/front.csv')
    if all(front['name'].values == idf['name'].values[:len(front)]):
        pass
    else:
        print('name mishmash')
        raise Exception('name mishmash')

    ##
    to_fill = front['front'].isnull().values
    #  from where to fill empty front cells
    if not to_fill[-1]:
        to_fill = len(to_fill)
    else:
        to_fill = np.where(~to_fill)[0][-1]+1

    changed = False
    if len(idf) >= to_fill:
        ynet = pd.read_csv('data/ynetlist.csv')
        yd = []
        for iy in range(len(ynet)):
            yd.append('|'.join([str(ynet[ynet.columns[5]][iy]).replace('nan','') + ' ' + str(ynet[ynet.columns[6]][iy]).replace('nan',''),
                           str(ynet['גיל'][iy]), str(ynet['מקום מגורים'][iy])]))
        otef = '|'.join(['זיקים', 'נתיב העשרה', 'כפר עזה', 'נחל עוז', 'שדרות', 'בארי', 'כיסופים', 'מפלסים'])
        for ii in range(to_fill, len(idf)):
            st = idf['story'][ii]
            yy = ''
            ff = ''
            id = '|'.join([idf['name'][ii], str(idf['age'][ii]), str(idf['from'][ii])])
            distance = [Levenshtein.distance(id, x) for x in yd]
            if min(distance) < 3:
                yrow = np.argmin(distance)
                yy = ynet['מידע על המוות'][yrow]
            if (type(re.search(otef, yy)) == re.Match) or \
                (type(re.search(otef, st)) == re.Match):
                ff = 'עוטף עזה'
            elif (type(re.search(r'נפל בקרב.+רצוע', yy)) == re.Match) or \
                 (type(re.search(r'נפל בקרב.+רצוע', st)) == re.Match):
                ff = 'עזה'
            elif 'לבנון' in yy or 'לבנון' in st:
                ff = 'לבנון'
            elif 'נרצח' in yy or 'נרצח' in st:
                ff = 'נרצח כאזרח'
            elif idf['death_date'][ii] > '2023-10-30' and ('הרצועה' in st or 'רצועת עזה' in st):
                ff = 'עזה'
            if len(yy) > 0 or len(ff) > 0:
                changed = True
            gdud = ''
            if 'גדוד' in st:
                stsplit = st[st.index('גדוד'):].split(' ')[:3]
                gdud = [x.replace(',','') for x in stsplit if x.replace(',','').isdigit()]
                if len(gdud) == 1:
                    gdud = gdud[0]
                else:
                    gdud = ''
            front.loc[ii] = [idf['name'][ii], st, yy, ff, gdud]
    front.to_csv('data/front.csv', index=False)
except:
    print('failed front update')