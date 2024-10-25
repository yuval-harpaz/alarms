"""Scrape data from IDF memorial site"""
import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np
import re
local = '/home/innereye/alarms/'

month_heb = ['ינואר', 'פברואר', 'מרץ', 'אפריל',
             'מאי', 'יוני', 'יולי', 'אוגוסט',
             'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']
if os.path.isdir(local):
    os.chdir(local)
    local = True
csv = 'data/deaths_idf.csv'
only_new = True
if only_new:
    dfprev = pd.read_csv('data/deaths_idf.csv')
    id = []
    for x in range(len(dfprev)):
        id.append('|'.join([dfprev['name'][x], str(dfprev['age'][x]), str(dfprev['from'][x]).replace('nan','')]))
    id = np.array(id)

# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:
try:
    with Display() as disp:
        try:
            browser = webdriver.Firefox()
        except:
            browser = webdriver.Chrome()
        already = 0
        data = []
        goon = True
        page = 0
        while goon:
            page += 1
            prev = len(data)
            url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
            browser.get(url)
            time.sleep(0.1)
            html = browser.page_source
            if page == 1:
                itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
                tot = html[itot-10:itot+10]
                tot = tot[tot.index('>')+1:]
                tot = int(tot[:tot.index(' ')])
            segs = html.split('ol-lg-6 col-md-6 wrap-item')
            for iseg in range(1, len(segs)):
                if goon:
                    seg = segs[iseg]
                    personal = seg[seg.index('href=')+5:]  # no more seg.index('aria-')
                    personal = personal[personal.index('"')+1:]
                    personal = personal[:personal.index('"')]
                    seg = seg[seg.index('solder-name'):]
                    # redate = re.search('202\d{1}\)', seg)
                    redate = re.search('\(\d{2} [^\d]+ \d{4}\)', seg)
                    if redate:
                        iyear = redate.start()
                        date = seg[redate.start()+1:redate.end()-1]
                        date = date.split(' ')
                        month = [x for x in range(12) if date[1][1:] in month_heb[x]][0]+1
                        date[1] = str(month).zfill(2)
                        date = '-'.join(date[::-1])
                    else:
                        date = ''
                    rank = seg[seg.index("small")+7:]
                    rank = rank[:rank.index('<')]
                    name = seg.split('\n')[2].strip()
                    print(name)
                    unit = seg.split('\n')[6].strip()
                    urlp = 'https://www.idf.il' + personal
                    browser.get(urlp)
                    htmlp = browser.page_source
                    if 'z"l' in htmlp:
                        htmle = htmlp[htmlp.index("small"):]
                        htmle = htmle[:htmle.index('z"l')]
                        en = htmle[::-1]
                        en = en[:en.index('>')][::-1].strip()
                    else:
                        en = np.nan
                    if 'אין מה לראות כאן' in htmlp:
                        urlp = np.nan
                    htmlp = htmlp[htmlp.index("small"):]
                    if name+',' in htmlp:
                        htmlp = htmlp[htmlp.index(name+','):]
                    elif name + ' (' in htmlp:
                        htmlp = htmlp[htmlp.index(name + ' ('):]
                    else:
                        if name[-6:]+',' in htmlp:
                            htmlp = htmlp[htmlp.index(name[-6:] + ','):]
                        elif '(' in name:
                            htmlp = htmlp[htmlp.index(name[name.index(')')+1:] + ','):]
                        elif name+' מ' in htmlp:
                            htmlp = htmlp[htmlp.index(name+' מ'):]
                            htmlp = htmlp.replace(name+' מ', name+','+' מ')
                        elif name+"'," in htmlp:
                            htmlp = htmlp[htmlp.index(name+"',"):]
                        elif name+' ז"ל'+',' in htmlp:
                            htmlp = htmlp[htmlp.index(name+' ז"ל'+','):]
                        elif name[:-1]+',' in htmlp:
                            htmlp = htmlp[htmlp.index(name[:-1] + ','):]
                        else:
                            print(name+' not found with ","')
                            os.system(f'echo "war23_idf_mem_all.py: {name}+, not in htmlp" >> code/errors.log')
                            htmlp = htmlp[:htmlp.index('בנופל')]
                            htmlp = name+htmlp.split(name)[-1]
                    if 'מדרגת' in htmlp:
                        raised = htmlp[htmlp.index('מדרגת')-7:]
                        raised = ' '+raised.split('<br><br>')[0].replace('>', '')
                        if len(raised) > 500:
                            raised = raised[:raised.index('<b')]
                    else:
                        raised = ''

                    if '<br><br>' in htmlp:
                        htmlp = htmlp[:htmlp.index('<br><br>')]
                    if len(htmlp) > 500:
                        print('insane')
                    if 'בנופ' in htmlp:
                        fro = htmlp.split(',')[1][2:]
                        ifro = htmlp.index(fro)
                        ifell = htmlp.index('בנופל')
                        age = int(htmlp[ifell - 3:ifell - 1])
                        story = htmlp[ifro + len(fro) + 2:ifell - 8]+'.'+raised
                        gender = htmlp[ifell - 6:ifell - 4].replace('בן', 'M').replace('בת', 'F')
                    else:
                        gender = ''
                        age = ''
                        fro = htmlp.split(',')[2][2:]
                        if 'בן' in htmlp:
                            g = 'בן'
                            gender = 'M'
                        elif 'בת' in htmlp:
                            g = 'בת'
                            gender = 'F'
                        age = htmlp[htmlp.index(g)+3:]
                        if ' ' in age:
                            age = age[:age.index(' ')]
                        if ',' in age:
                            age = age[:age.index(',')]
                        story = ','.join([x for x in htmlp.split(',')[3:] if x[:4] != ' בן '])
                    if only_new and ('|'.join([name, str(age), str(fro)]) in id or name in id[-1]):
                        goon = False
                    else:
                        data.append([date, name, rank, unit, gender, age, fro, story, np.nan, urlp, en])
            if len(data) == prev:  # new page with no names
                goon = False
            # else:
            #     print(len(data))
        # browser.close()
        browser.quit()
    print(f'new IDF deaths: {len(data)}')
    ##
    if len(data) > 0:
        df = pd.DataFrame(data, columns=['death_date', 'name', 'rank', 'unit', 'gender', 'age', 'from','story', 'pid',
                                         'webpage', 'eng'])
        df = df.iloc[::-1]
        df = pd.concat([dfprev, df])
        df = df.reset_index(drop=True)
        bads = df["story"].str.findall(r'&.{4};')
        if any(bads):
            ibad = [x for x in range(len(bads)) if len(bads.values[x]) > 0]
            for jbad in ibad:
                if list(np.unique(bads.values[jbad])) == ['&nbsp;']:
                    df.at[jbad, 'story'] = df['story'][jbad].replace('&nbsp;', ' ')
                else:
                    raise Exception('got to replace &xxx; with something')
        df.to_csv(csv, index=False)
        if len(df) == tot:
            pass
        else:
            print(f'total should be {tot}, instead {len(df)}')
except Exception as e:
    print('war23_idf_mem_all.py failed')
    a = os.system('echo "war23_idf_mem_all.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')
