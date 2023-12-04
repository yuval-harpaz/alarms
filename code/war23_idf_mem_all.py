import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np

local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True
csv = 'data/deaths_idf.csv'
only_new = True
if only_new:
    prev = pd.read_csv('data/deaths_idf.csv')
    id = []
    for x in range(len(prev)):
        id.append('|'.join([prev['name'][x], str(prev['age'][x]), str(prev['from'][x])]))
    id = np.array(id)

# dfprev = pd.read_csv(csv)
##
# def get_deaths():
# try:
try:
    with Display() as disp:
        try:
            browser = webdriver.Chrome()
        except:
            print('no chrome? trying firefox')
            browser = webdriver.Firefox()
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
                    personal = seg[seg.index('href=')+5:seg.index('aria-')]
                    personal = personal[personal.index('"')+1:]
                    personal = personal[:personal.index('"')]
                    seg = seg[seg.index('solder-name'):]
                    if '2023)' in seg:
                        iyear = segs[iseg].index('2023)')
                        date = segs[iseg][iyear - 6:iyear + 4]
                        date = '-'.join(date.split('.')[::-1])
                    else:
                        date=''
                    # seg = segs[iseg][:iyear+5]
                    rank = seg[seg.index("small")+7:]
                    rank = rank[:rank.index('<')]
                    name = seg.split('\n')[2].strip()
                    print(name)
                    # if name in dfprev['name'].values:
                    #     already += 1
                    #     print('already ' + name)
                    #     if already == 2:
                    #         goon = False
                    unit = seg.split('\n')[6].strip()
                    urlp = 'https://www.idf.il' + personal
                    # urlp = 'https://www.idf.il/נופלים/חללי-המלחמה/'+'-'.join(name.split(' '))
                    # for rep in ["'"]:
                    #     urlp = urlp.replace(rep, '-')
                    # for rep in ["(", ")"]:
                    #     urlp = urlp.replace(rep, '')
                    browser.get(urlp)
                    htmlp = browser.page_source
                    htmlp = htmlp[htmlp.index("small"):]
                    if name+',' in htmlp:
                        htmlp = htmlp[htmlp.index(name+','):]
                    else:
                        if name[-6:]+',' in htmlp:
                            htmlp = htmlp[htmlp.index(name[-6:] + ','):]
                        elif '(' in name:
                            htmlp = htmlp[htmlp.index(name[name.index(')')+1:] + ','):]
                        elif name+' מ' in htmlp:
                            htmlp = htmlp[htmlp.index(name+' מ'):]
                            htmlp = htmlp.replace(name+' מ',name+','+' מ')
                        elif name+"'," in htmlp:
                            htmlp = htmlp[htmlp.index(name+"',"):]
                        else:
                            print(name+' not found with ","')
                            os.system(f'echo "war23_idf_mem.py: {name}+, not in htmlp" >> code/errors.log')
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
                        fro = ''
                        age = 0
                        story = ''
                        gender = ''
                        if 'נפטר' in htmlp:
                            fro = htmlp.split(',')[1][2:]
                            ifro = htmlp.index(fro)
                            story = htmlp[ifro + len(fro) + 2:] + raised
                            # story = story[:story.index('\n')]
                        else:
                            msg = 'failed for ' + urlp.split('/')[-2]
                            print(msg)
                            os.system(f'echo "war23_idf_mem.py: {msg}" >> code/errors.log')
                    if only_new and '|'.join([name, str(age), fro]) in id:
                        goon = False
                    else:
                        data.append([date, name, rank, unit, gender, age, fro, story])
            if len(data) == prev:  # new page with no names
                goon = False
            else:
                print(len(data))
        browser.close()
    print(f'new IDF deaths: {len(data)}')
    ##
    if len(data) > 0:
        df = pd.DataFrame(data, columns=['death_date', 'name', 'rank', 'unit', 'gender', 'age', 'from','story'])
        df = df.iloc[::-1]
        df = pd.concat([prev, df])
        df.to_csv(csv, index=False)
        if len(df) == tot:
            pass
        else:
            print(f'total should be {tot}, instead {len(df)}')
except Exception as e:
    print('war23_idf_mem.py failed')
    a = os.system('echo "war23_idf_mem.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')
    