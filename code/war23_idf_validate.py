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
# only_new = True
# if only_new:
#     dfprev = pd.read_csv('data/deaths_idf.csv')
    # id = []
    # for x in range(len(dfprev)):
    #     id.append('|'.join([dfprev['name'][x], str(dfprev['age'][x]), str(dfprev['from'][x]).replace('nan','')]))
    # id = np.array(id)

# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:
browser = webdriver.Firefox()
##
df = pd.read_csv('data/deaths_idf.csv')
# with Display() as disp:
start = 0
bugs = ''
for ii in range(start, len(df)):
    print(ii)
    browser.get(df['webpage'][ii])
    htmlp = browser.page_source
    if df['name'][ii] not in htmlp.replace("'", "׳"):
        pattern = 'title itemprop="name"'
        jj = htmlp.index(pattern)
        name = htmlp[jj+len(pattern)+1:]
        name = htmlp[jj+len(pattern)+1:]
        name = name[:name.index(' |')]
        message = f'{df["name"][ii]} ({df["pid"][ii]}) should be {name}'
        print(message)
        bugs = bugs + message + '\n'
    gen = df['gender'][ii].replace('M', 'בן ').replace('F', 'בת ')
    if gen+str(df['age'][ii]) not in htmlp:
        pattern = gen+"\d{2}"
        results = re.search(pattern, htmlp)
        if results is None:
            if ii in [355]:
                pass
            else:
                message = f'no age for {df["webpage"][ii].split("/")[-2]} ({df["pid"][ii]})'
                print(message)
                bugs = bugs + message + '\n'
        else:
            age = htmlp[results.span()[0]+3:results.span()[0]+5]
            message = f'age for {name} ({df["pid"][ii]}) should be {age}'
            print(message)
            bugs = bugs + message + '\n'

    redate = re.search('\(\d{2} [^\d]+ \d{4}\)', htmlp)
    if redate:
        iyear = redate.start()
        date = htmlp[redate.start()+1:redate.end()-1]
        date = date.split(' ')
        month = [x for x in range(12) if date[1][1:] in month_heb[x]][0]+1
        date[1] = str(month).zfill(2)
        date = '-'.join(date[::-1])
        if df['death_date'][ii] != date:
            message = f'date for {df["webpage"][ii].split("/")[-2]} ({df["pid"][ii]}) should be {date}'
            print(message)
            bugs = bugs + message + '\n'
##
for ii in range(len(df)):
    name = df['name'][ii]
    if "'" in name:
        df.at[ii, 'name'] = name.replace("'","׳")
df.to_csv('data/deaths_idf.csv', index=False)
##  TODO: make sure names ages and dates are okay in DB, also נרצח כאזרח
db = pd.read_csv('data/oct7database.csv')
pids = db['pid'].values
for ii in range(len(df)):
    pid = df['pid'][ii]
    row = np.where(pids == pid)[0][0]
    if db['Age'][row] != df['age'][ii]:
        db.at[row, 'Age'] = df['age'][ii]
    if db['Death date'][row] != df['death_date'][ii]:
        if db['Death date'][row] == db['Event date'][row]:
            db.at[row, 'Event date'] = df['death_date'][ii]
        # else:
        #     print(f'check dates for {pid}')
        db.at[row, 'Death date'] = df['death_date'][ii]
    first = db['שם פרטי'][row]
    if ' ' not in first and first != df['name'][ii].split(' ')[0]:
        print(f'{pid} {first}')
        # db.at[row, 'Age'] = df['age'][ii]
    last = db['שם משפחה'][row]
    if "'" in last:
        last = last.replace("'", "׳")
        db.at[row, 'שם משפחה'] = last
    if ' ' not in last and last != df['name'][ii].split(' ')[-1]:
        if pid not in [1643]: # ריבלין
            print(f'{pid} {last}')
db.to_csv('data/oct7database.csv', index=False)

##
db = pd.read_csv('data/oct7database.csv')
front = pd.read_csv('data/front.csv')
cit = np.where(front['front'] == 'נרצח כאזרח')[0]
for ii in cit:
    pid = df['pid'][ii]
    row = np.where(pids == pid)[0][0]
    role = db['Role'][row]
    if role != 'אזרח' and 'kidnapped' not in db['Status'][row] and pid not in [2064]:
        print(pid)
        db.at[row, 'Role'] = 'אזרח'
##
            ##
    # if 'z"l' in htmlp:
    #     htmle = htmlp[htmlp.index("small"):]
    #     htmle = htmle[:htmle.index('z"l')]
    #     en = htmle[::-1]
    #     en = en[:en.index('>')][::-1].strip()
    # already = 0
    # data = []
    # goon = True
    # page = 0
    # while goon:
    #     page += 1
    #     prev = len(data)
    #     url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
    #     browser.get(url)
    #     time.sleep(0.1)
    #     html = browser.page_source
    #     if page == 1:
    #         itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
    #         tot = html[itot-10:itot+10]
    #         tot = tot[tot.index('>')+1:]
    #         tot = int(tot[:tot.index(' ')])
    #     segs = html.split('ol-lg-6 col-md-6 wrap-item')
    #     for iseg in range(1, len(segs)):
    #         if goon:
    #             seg = segs[iseg]
    #             personal = seg[seg.index('href=')+5:]  # no more seg.index('aria-')
    #             personal = personal[personal.index('"')+1:]
    #             personal = personal[:personal.index('"')]
    #             seg = seg[seg.index('solder-name'):]
                # redate = re.search('202\d{1}\)', seg)
                # redate = re.search('\(\d{2} [^\d]+ \d{4}\)', seg)
                # if redate:
                #     iyear = redate.start()
                #     date = seg[redate.start()+1:redate.end()-1]
                #     date = date.split(' ')
                #     month = [x for x in range(12) if date[1][1:] in month_heb[x]][0]+1
                #     date[1] = str(month).zfill(2)
                #     date = '-'.join(date[::-1])
                # else:
                #     date = ''
                # rank = seg[seg.index("small")+7:]
                # rank = rank[:rank.index('<')]
                # name = seg.split('\n')[2].strip()
                # print(name)
                # unit = seg.split('\n')[6].strip()
                # urlp = 'https://www.idf.il' + personal
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
    browser.close()
print(f'new IDF deaths: {len(data)}')
##
if len(data) > 0:
    df = pd.DataFrame(data, columns=['death_date', 'name', 'rank', 'unit', 'gender', 'age', 'from','story', 'pid',
                                     'webpage', 'eng'])
    df = df.iloc[::-1]
    df = pd.concat([dfprev, df])
    df.to_csv(csv, index=False)
    if len(df) == tot:
        pass
    else:
        print(f'total should be {tot}, instead {len(df)}')
# except Exception as e:
#     print('war23_idf_mem_all.py failed')
#     a = os.system('echo "war23_idf_mem_all.py failed" >> code/errors.log')
#     b = os.system(f'echo "{e}" >> code/errors.log')
