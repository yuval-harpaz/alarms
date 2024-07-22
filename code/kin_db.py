
import pandas as pd
import os
import numpy as np

db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
residence = db['residence'].values
evloc = db['מקום האירוע'].values
keep = []
for ii in range(len(db)):
    name = db['שם משפחה'][ii]
    namesp = name.split(' ')
    matches = False
    candidates = np.where((residence == db['residence'][ii]) | (evloc == db['מקום האירוע']))[0]
    for jj in candidates:
        if jj not in keep and jj != ii:
            compare = db['שם משפחה'][jj]
            keepit = False
            if compare == name:
                keepit = True
                matches = True
            else:
                compare = [x for x in compare if len(x) > 2]
                if len(compare):
                    for comp in compare:
                        # cond = (len(compare) == 1 | len(comp) > 2) and (comp in name)
                        # if (len(compare) == 1) | len(comp) > 2:
                        #     try:
                        #         idx = name.index(comp)
                        if comp in namesp:
                            keepit = True
                            matches = True
                            # except:
                            #     pass
            if keepit:
                if matches and ii not in keep:
                    keep.append(ii)
                keep.append(jj)

##
# xlsx = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
df = pd.DataFrame(columns=['pid','name','residence','event location','event date', 'status'])
for kk in range(len(keep)):
    pid = db['pid'][keep[kk]]
    name = (db['שם פרטי'][keep[kk]] + ';' +
            str(db['שם נוסף'][keep[kk]]) + ';' +
            db['שם משפחה'][keep[kk]]
            ).replace('nan', '').replace(';;', ' ').replace(';', ' ')
    if db['pid'][keep[kk]] != pid:
        raise Exception('pid not the same for ' + str(keep[kk]))
    residence = db['residence'][keep[kk]]
    loc = db['מקום האירוע'][keep[kk]]
    date = str(db['Event date'][keep[kk]])[:10]
    status = db['Status (oct7map)'][keep[kk]]
    df.loc[len(df)] = [pid, name, residence, loc, date, status]

df.to_excel('~/Documents/names_by_common_location.xlsx', index=False)

