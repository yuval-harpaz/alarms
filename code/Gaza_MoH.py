# from matplotlib import colors
import pandas as pd
import numpy as np
import os
##
df = pd.read_excel('/home/innereye/Documents/Gaza_MoH.xlsx')
names = df['name'].values
nameu = np.sort(np.unique(names))
len(df)-len(nameu)

ids = df['ID'].values
for ii in range(len(ids)):
    if type(ids[ii]) != int:
        ids[ii] = 0

for ii, name in enumerate(nameu):
    idx = np.where(names == name)[0]
    if len(idx) > 1:
        okay = idx[ids[idx] > 0]
        if len(okay) > 0:
            okay = okay[0]
            bad = idx[idx != okay]
        else:
            bad = idx
        for jj in bad:
            comment = str(df['comment'][jj]).replace('nan','')+' duplicate'
            df.at[jj, 'comment'] = comment
            # print(f"{ids[jj]} {df['age'][jj]}")
idsu = np.sort(np.unique(ids[ids > 0]))
for ii, id in enumerate(idsu):
    idx = np.where(ids == id)[0]
    if len(idx) > 1:
        # print(ii)
        okay = []
        for jj in idx:
            okay.append('duplicate' not in str(df['comment'][jj]))
        okay = idx[okay]
        if len(okay) > 0:
            okay = okay[0]
            bad = idx[idx != okay]
            for jj in bad:
                comment = str(df['comment'][jj]).replace('nan','')+' duplicate'
                df.at[jj, 'comment'] = comment
            # print(f"{ids[jj]} {df['age'][jj]}")

df.to_excel('/home/innereye/Documents/Gaza_MoH_comments.xlsx')

##
from matplotlib import pyplot as plt
df = pd.read_excel('/home/innereye/Documents/Gaza_MoH_comments.xlsx')
okay = df['comment'].isnull() & (~df['age'].isnull()) & (df['ID'] > 0)
okay = okay.values

##
millions = [4, 7, 8, 9]
plt.figure()
for ii in range(len(millions)):
    ifrom = millions[ii]*10**8
    ito = (millions[ii]+1)*10**8
    plt.subplot(2, 2, ii+1)
    group = okay & (df['ID'].values >= ifrom) & (df['ID'].values < ito)
    plt.plot(df['ID'][group], df['age'][group], '.')
    plt.xlim(ifrom, ito)
    plt.title(f'ID from {ifrom} to {ito}')
    plt.ylabel('age')
    plt.xlabel('ID')
    plt.ylim(0, 105)
    plt.grid()

##
def control_digit(id_num):
    assert isinstance(id_num, str) and len(id_num) == 8
    total = 0
    for i in range(8):
        val = int(id_num[i]) # converts char to int
        if i%2 == 0:        # even index (0,2,4,6,8)
            total += val
        else:               # odd index (1,3,5,7,9)
            if val < 5:
                total += 2*val
            else:
                total += ((2*val)%10) + 1 # sum of digits in 2*val
                                          # 'tens' digit must be 1
    total = total%10            # 'ones' (rightmost) digit
    check_digit = (10-total)%10 # the complement modulo 10 of total
                                # for example 42->8, 30->0
    return str(check_digit)
controlled = np.zeros(len(df))
controlled[:] = np.nan
for ii in range(len(df)):
    if okay[ii]:
        num = str(df['ID'][ii])
        if len(num) == 9:
            if control_digit(num[:-1]) == num[-1]:
                controlled[ii] = 1
            else:
                comment = str(df['comment'][ii]).strip('nan') + 'bad control'
                df.at[ii, 'comment'] = comment
                controlled[ii] = 0
        else:
            comment = str(df['comment'][ii]).strip('nan') + 'bad n digits'
            df.at[ii, 'comment'] = comment
            controlled[ii] = 0

millions = [4, 7, 8, 9]
plt.figure()
for ii in range(len(millions)):
    ifrom = millions[ii]*10**8
    ito = (millions[ii]+1)*10**8
    plt.subplot(2, 2, ii+1)
    group = okay & (df['ID'].values >= ifrom) & (df['ID'].values < ito)
    for cont in [1]: #[0, 1]:
        plt.plot(df['ID'][group & (controlled == cont)], df['age'][group & (controlled == cont)], '.'+'rb'[cont])
    plt.xlim(ifrom, ito)
    plt.title(f'ID from {ifrom} to {ito}')
    plt.ylabel('age')
    plt.xlabel('ID')
    plt.ylim(0, 105)
    plt.grid()

##
np.sum((controlled == 0) & (df['source'].values == 'report from family'))