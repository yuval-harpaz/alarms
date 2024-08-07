import pandas as pd
import numpy as np
dfs = []
for iter in [0, 1]:
    db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
    if iter == 0:
        first_days = np.array([str(x)[:10] for x in db['Event date'].values]) < '2023-10-10'
        db = db[first_days]
        db = db.reset_index(drop=True)
        suf = ''
    else:
        suf = '_all'
    residence = db['residence'].values
    evloc = np.array([str(x).split(';')[0] for x in db['מקום האירוע'].values])
    keep = []
    for ii in range(len(db)):
        name = db['שם משפחה'][ii]
        namesp = name.split(' ')
        matches = False
        candidates = np.where((residence == db['residence'][ii]) | (evloc == db['מקום האירוע'][ii]))[0]
        for jj in candidates:
            if jj not in keep and jj != ii:
                compare = db['שם משפחה'][jj]
                keepit = False
                if compare == name:
                    keepit = True
                    matches = True
                else:
                    compare = [x for x in compare.replace('-', ' ').split(' ') if len(x) > 2]
                    if len(compare):
                        for comp in compare:
                            if comp in namesp:
                                keepit = True
                                matches = True
                if keepit:
                    if matches and ii not in keep:
                        keep.append(ii)
                    keep.append(jj)

    ##
    # xlsx = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
    df = pd.DataFrame(columns=['pid', 'name', 'first name', 'last name',
                               'residence', 'event location', 'event date', 'status'])
    for kk in range(len(keep)):
        pid = db['pid'][keep[kk]]
        name = (db['שם פרטי'][keep[kk]] + ';' +
                str(db['שם נוסף'][keep[kk]]) + ';' +
                db['שם משפחה'][keep[kk]]
                ).replace('nan', '').replace(';;', ' ').replace(';', ' ')
        first = db['שם פרטי'][keep[kk]]
        last = db['שם משפחה'][keep[kk]]
        if db['pid'][keep[kk]] != pid:
            raise Exception('pid not the same for ' + str(keep[kk]))
        residence = db['residence'][keep[kk]]
        loc = db['מקום האירוע'][keep[kk]].split(';')[0]
        date = str(db['Event date'][keep[kk]])[:10]
        status = db['Status (oct7map)'][keep[kk]]
        df.loc[len(df)] = [pid, name, first, last, residence, loc, date, status]

    df.to_excel(f'~/Documents/names_by_common_location{suf}.xlsx', index=False)
    dfs.append(df)

keep = []
pid = dfs[0]['pid'].values
for ii in range(len(dfs[1])):
    if dfs[1]['pid'][ii] not in pid:
        keep.append(True)
    else:
        keep.append(False)
dif = dfs[1][keep]
dif.to_excel(f'~/Documents/names_by_common_location_dif.xlsx', index=False)