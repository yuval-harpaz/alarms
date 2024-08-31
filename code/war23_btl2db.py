import pandas as pd
import numpy as np
import datetime
# db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
# idf = pd.read_csv('data/deaths_idf.csv')
# map = pd.read_csv('data/oct_7_9.csv')

# kidn = pd.read_csv('data/kidnapped.csv')
def get_idx(x, vec):
    i = np.where(vec == x)[0]
    if len(i) == 0:
        i = None
    elif len(i) == 1:
        i = i[0]
    else:
        raise Exception(f'too many {x} in vec')
    return i


def intize(m):
    if (type(m) == float or type(m) == np.float64) and ~np.isnan(m):
        m = int(m)
    return m


theday = datetime.date(2023, 10, 7)
##
btl = pd.read_excel('~/Documents/btl_yael_netzer.xlsx')
db = pd.read_csv('data/oct7database.csv')
pids = db['pid'].values
bid = btl['BTL_ID'].values
skip = [2014, 60, 619]
missing = []
naming = pd.DataFrame(columns=['pid', 'db', 'btl', 'page'])
for ii in range(len(pids)):
    if db['pid'][ii] not in skip:
        if type(db['הנצחה'][ii]) == str and 'laad' in db['הנצחה'][ii]:
            id = int(db['הנצחה'][ii].split('ID=')[-1])
            row = get_idx(id, bid)
            if row is not None:
                born = btl['BirthDate'][row]
                if type(born) == datetime.datetime:
                    age = theday.year - born.year - ((theday.month, theday.day) < (born.month, born.day))
                else:
                    age = intize(btl['Age'][row])
                existing = str(intize(db['Age'][ii]))
                if existing != str(age) and str(age) != 'nan':
                    db.at[ii, 'Age'] = int(age)
                    print(f"{ii} {pids[ii]} {db['first name'][ii]} {db['last name'][ii]} {existing} vs {age}")
                first = str(btl['FirstName'][row]).replace("'", '׳')
                if 'n' not in  first and db['שם פרטי'][ii] not in first:
                    # print(f"{ii} {pids[ii]} {db['שם פרטי'][ii]} vs {first}")
                    naming.loc[len(naming)] = [pids[ii], db['שם פרטי'][ii], first, db['הנצחה'][ii]]
                last = str(btl['LastName'][row]).replace("'", '׳')
                if 'n' not in last and db['שם משפחה'][ii] not in last:
                    # print(f"{ii} {pids[ii]} {db['שם משפחה'][ii]} vs {last}")
                    naming.loc[len(naming)] = [pids[ii], db['שם משפחה'][ii], last, db['הנצחה'][ii]]
                nick = str(btl['NickName'][row]).replace("'", '׳')
                if 'n' not in nick and nick != str(db['כינוי'][ii]):
                    # print(f"{ii} {pids[ii]} {db['כינוי'][ii]} vs {nick}")
                    naming.loc[len(naming)] = [pids[ii], db['כינוי'][ii], nick, db['הנצחה'][ii]]
            else:
                # print(f"{ii} {id} no row")
                missing.append(id)
print('missing:')
print(' '.join(sorted([str(x) for x in missing])))
##
naming.to_excel('~/Documents/btl_naming_issues.xlsx', index=False)
db.to_csv('data/oct7database.csv', index=False)
##
included = []
for hantz in db['הנצחה']:
    if type(hantz) == str and 'laad' in hantz:
        id = int(hantz.split('ID=')[-1])
        included.append(id)
extra = np.zeros(len(btl), bool)
for ii in range(len(btl)):
    if btl['BTL_ID'][ii] not in included:
        extra[ii] = True
dfe = btl[extra]
dfe.to_excel('~/Documents/btl_extra.xlsx', index=False)
##
db = pd.read_csv('data/oct7database.csv')
bugs = ''
for ii in range(len(pids)):
    if db['pid'][ii] not in skip:
        if type(db['הנצחה'][ii]) == str and 'laad' in db['הנצחה'][ii]:
            id = int(db['הנצחה'][ii].split('ID=')[-1])
            row = get_idx(id, bid)
            if row:
                if type(btl['EventDate'][row]) == str and db['Event date'][ii] != str(btl['EventDate'][row]):
                    print(str(db['Event date'][ii])+' '+btl['EventDate'][row])
                date = btl['DeathDate'][row]
                if type(date) == datetime.datetime:
                    date = date.strftime('%Y-%m-%d')
                else:
                    date = str(date)
                    if len(date) > 4:
                        date = '-'.join([x.zfill(2) for x in date.split('-')])
                # if len(date) > 10:
                #     date = date[:10]
                datedb = db['Death date'][ii]
                if date != 'NaT' and datedb != date:
                    message = f'death date for {db["שם פרטי"][ii]} {db["שם משפחה"][ii]} ({db["pid"][ii]}) should be {date}'
                    print(message)
                    bugs = bugs + message +'\n'
                    # print(str(ii) + ' ' + str(db['pid'][ii]) + ' ' + datedb + ' ' + date)
                    # if date[:4] == '2023' and datedb[:4] == '2024' and date[4:] == datedb[4:]:
                    #     if db['Event date'][ii] == db['Death date'][ii]:
                    #         print(str(db['pid'][ii]) + ' ' + db['last name'][ii]+' '+date)
                    #     else:
                    #         print('no can fix')
                    # else:
                    #     pass
                        # print(str(ii)+' '+str(db['pid'][ii])+' '+datedb+' '+date)


##
#         else:
#             age.append(np.nan)
#     elif pid[ii] in map['pid'].values:
#         row = get_idx(pid[ii], map['pid'].values)
#         age.append(intize(map['age'][row]))
#     elif pid[ii] in kidn['pid'].values:
#         row = get_idx(pid[ii], kidn['pid'].values)
#         age.append(intize(kidn['age'][row]))
#     else:
#         age.append(np.nan)
#
# db['Age'] = age
# db.to_csv('~/Documents/age.csv', index=False)
