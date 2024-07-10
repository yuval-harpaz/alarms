import pandas as pd
import os
import numpy as np
import re
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
## load data and run sanity checks
# csv = 'data/deaths_idf.csv'
only_new = False
# if only_new:
idf = pd.read_csv('data/deaths_idf.csv')
missing = np.sum(idf['webpage'].isnull())
if missing:
    raise Exception(f'{missing} idf missing webpage')
wpu = np.unique(idf['webpage'])
if len(wpu) < len(idf):
    raise Exception('idf webpage not usinque')
db = pd.read_csv('data/oct7database.csv')
for ii in np.where([x in idf['pid'].values for x in db['pid'].values])[0]:
    row = np.where(idf['pid'].values == db['pid'][ii])[0][0]
    if db['הנצחה'][ii] != idf['webpage'][row]:
        raise Exception('different webpages for pid ' + str(db['pid'][ii]))

inew = np.where([x not in db['הנצחה'].values for x in idf['webpage'].values])[0]
for ii in inew:
    url = idf['webpage'][ii]
    if url in db['הנצחה'].values:
        raise Exception(f'url already in db : {url}')
##
db = pd.read_csv('data/oct7database.csv')
ranks = ['sergeant', 'sergent', 'captain', 'lieutenant', 'major', 'colonel',
         'chief warrant officer', 'warrant officer', 'corporal']
for ii in inew:
    idb = len(db)
    db.at[idb, 'pid'] = np.max(db['pid']+1)
    db.at[idb, 'Status'] = 'killed on duty'
    db.at[idb, 'Gender'] = idf['gender'][ii]
    db.at[idb, 'הנצחה'] = idf['webpage'][ii]
    nameheb = idf['name'][ii].split(' ')
    db.at[idb, 'שם פרטי'] = nameheb[0]
    db.at[idb, 'שם משפחה'] = nameheb[-1]
    if len(nameheb) > 2:
        db.at[idb, 'שם נוסף'] = ' '.join(nameheb[1:-1])
    story = idf['story'][ii]
    if 'פצע' in story or 'נפטר' in story:
        same_day = False
    else:
        same_day = True
    db.at[idb, 'Death date'] = idf['death_date'][ii]
    if same_day:
        db.at[idb, 'Event date'] = idf['death_date'][ii]
    if 'רצוע' in story:
        if re.search(r'מרכז.רצוע', story, re.UNICODE):
            db.at[idb, 'מקום האירוע'] = 'מרכז רצועת עזה'
        elif re.search(r'דרום.רצוע', story, re.UNICODE):
            db.at[idb, 'מקום האירוע'] = 'דרום רצועת עזה'
        elif re.search(r'צפון.רצוע', story, re.UNICODE):
            db.at[idb, 'מקום האירוע'] = 'צפון רצועת עזה'
        db.at[idb, 'Event location class'] = 'idf'
        db.at[idb, 'Event location'] = db['מקום האירוע'][idb]
        if same_day:
            db.at[idb, 'מקום המוות'] = db['מקום האירוע'][idb]
    en = idf['eng'][ii]
    name = ''
    if type(en) == str:
        if '(res.)' in en:
            name = en[en.index('(res.)') + 6:].strip()
        elif 'class' in en.lower():
            name = en[en.lower().index('class') + 5:].strip()
        else:
            rank = [x for x in ranks if x in en.lower()]
            if len(rank) > 0:
                name = en[en.lower().index(rank[0]) + len(rank[0]):].strip()
            else:
                print(en)
    if len(name) > 0:
        name = name.split(' ')
        db.at[idb, 'first name'] = name[0]
        db.at[idb, 'last name'] = name[-1]
        if len(name) > 2:
            db.at[idb, 'middle name'] = ' '.join(name[1:-1])

db.to_csv('data/tmp_oct7database.csv', index=False)
##
# csv = 'data/deaths_idf.csv'
# only_new = False
# # if only_new:
# dfprev = pd.read_csv('data/deaths_idf.csv')
# dfdb = pd.read_csv('data/oct7database.csv')
# nopage = np.where(dfprev['webpage'].isnull())[0]
# for ii in nopage:
#     row = np.where(dfdb['pid'].values == dfprev['pid'][ii])[0]
#     if len(row) == 1:
#         print(ii)
#         url = dfdb['הנצחה'][row[0]]
#         dfprev.at[ii, 'webpage'] = url
# dfprev.to_csv('data/deaths_idf.csv', index=False)
# # dfprev = pd.read_csv(csv)
# ##
# # def get_deaths():
# # try:
#
#
# browser = webdriver.Firefox()
# already = 0
# urls = []
# eng = []
# goon = True
# page = 0
# for page in range(1, 100):
#     # prev = len(data)
#     url = 'https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%94%D7%9E%D7%9C%D7%97%D7%9E%D7%94/?page='+str(page)
#     browser.get(url)
#     time.sleep(0.1)
#     html = browser.page_source
#     # if page == 1:
#     #     itot = html.index('חללי המלחמה ששמותיהם הותרו לפרסום</h')
#     #     tot = html[itot-10:itot+10]
#     #     tot = tot[tot.index('>')+1:]
#     #     tot = int(tot[:tot.index(' ')])
#     segs = html.split('ol-lg-6 col-md-6 wrap-item')
#     for iseg in range(1, len(segs)):
#         if goon:
#             seg = segs[iseg]
#             personal = seg[seg.index('href=')+5:]  # no more seg.index('aria-')
#             personal = personal[personal.index('"')+1:]
#             personal = personal[:personal.index('"')]
#             urlp = 'https://www.idf.il' + personal
#             for rep in ["'"]:
#                 urlp = urlp.replace(rep, '-')
#             for rep in ["(", ")"]:
#                 urlp = urlp.replace(rep, '')
#             browser.get(urlp)
#             htmlp = browser.page_source
#             if 'אין מה לראות כאן' in htmlp:
#                 urls.append('')
#                 eng.append('')
#             else:
#                 urls.append(urlp)
#                 if 'z"l' in htmlp:
#                     htmlp = htmlp[htmlp.index("small"):]
#                     htmlp = htmlp[:htmlp.index('z"l')]
#                     en = htmlp[::-1]
#                     en = en[:en.index('>')][::-1].strip()
#                     eng.append(en)
#                 else:
#                     eng.append('')
# df = pd.DataFrame(eng, columns=['name'])
# df['url'] = urls
# df = df[::-1]
# df.to_csv('data/tmp_idf_eng.csv', index=False)
#
# ##
# df = pd.read_csv('data/tmp_idf_eng.csv')
# # db = pd.read_csv('data/deaths_idf.csv')
# db = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
# # name = []
# # for x in range(len(db)):
# #     name.append(db['שם פרטי'][x] + ' ' + str(db['שם נוסף'][x]) + ' ' + db['שם משפחה'][x])
# #     name[-1] = name[-1].replace(' nan', '')
# # name = np.array(name)
# for ii in range(len(df)):
#     row = np.where(np.array([x in df['heb'][ii] for x in db['שם פרטי']]) &
#                    np.array([x in df['heb'][ii] for x in db['שם משפחה']]))[0]
#     if len(row) == 1:
#         row = row[0]
#         df.at[ii, 'pid'] = db['pid'][row]
#
# pid = df['pid'].values
# pidu = np.unique(pid)
# dbpid = db['pid'].values
# for ii in range(len(df)):
#     row = np.where(dbpid == df['pid'][ii])[0][0]
#     db.at[row, 'הנצחה'] = df['url'][ii]
#
# null = np.where(db['הנצחה'].isnull())[0]
# for dbr in null:
#     pid = db['pid'][dbr]
#     crr = np.where(cref['oct7map_pid'] == pid)[0]
#     if len(crr) == 1:
#         btl_id = cref['btl_id'].values[crr[0]]
#         if ~np.isnan(btl_id):
#             laad = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Page/Default.aspx?ID='+str(int(btl_id))
#             db.at[dbr, 'הנצחה'] = laad
#
# db.to_csv('tmp.csv', index=False)