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
##
from translate import Translator
def translate_names(names):
    translator= Translator(to_lang="en", from_lang="ar")
    translated_names = [translator.translate(name) for name in names]
    return translated_names
# Example usage

df = pd.read_excel('/home/innereye/Documents/Gaza_MoH_comments.xlsx')

arab = df.loc[1]['name']
arab = [x for x in arab.split(' ') if len(x) > 1]
translate_names(arab)

##
from googletrans import Translator

def translate_names(names):
    translator = Translator()
    translated_names = [translator.translate(name, src='ar', dest='en').text for name in names]
    return translated_names

# Example usage
arabic_names = ["محمد", "فاطمة", "علي"]
english_names = translate_names(arabic_names)
print(english_names)

##
df = pd.read_excel('/home/innereye/Documents/Gaza_MoH_eng.xlsx')
names = list(df['name'])
# names = names[:3]
start = np.where(df['google_eng'].isnull())[0][0]
print('translating')
for ii in range(start, len(names)):
    trans = translate_names([names[ii]])
    df.at[ii, 'google_eng'] = trans
    if ii%100 == 0:
        df.to_excel('/home/innereye/Documents/Gaza_MoH_eng.xlsx', index=False)
        print(ii)

##
okay = df['comment'].isnull() & (~df['age'].isnull()) & (df['ID'] > 0)
okay = okay.values
millions = [4, 7, 8, 9]
plt.figure()
for ii in range(len(millions)):
    ifrom = millions[ii]*10**8
    ito = (millions[ii]+1)*10**8
    plt.subplot(2, 2, ii+1)
    group = okay & (df['ID'].values >= ifrom) & (df['ID'].values < ito)
    plt.plot(df['ID'][group], df['age'][group], '.'+'b')
    x = [ifrom, ifrom+50000000, ito]
    xst = [str(x) for x in x]
    plt.xticks(x, xst)
    plt.xlim(ifrom, ito)
    plt.text(ifrom+50000000, 95,  f'ID from {ifrom} to {ito}', ha='center')
    plt.ylabel('age')
    plt.xlabel('ID')
    plt.ylim(0, 105)
    plt.grid()

##
ID = df['ID'].values
age = df['age'].values

# -28x - 45000000y + 12550000000 = 0
y = (12550000000 - 28*ID)/45000000
g1 = np.abs(age - y) < 5  # linear
g1[(ID > 800000000) & (ID < 804620000) & (age < 45.5) & (age > 28)] = True
g1[(ID > 900000000) & (ID < 910620000) & (age < 51) & (age > 37)] = True
g2 = ((ID > 410000000) & (ID < 417000000)) | ((ID > 452000000) & (ID < 480000000)) | ((ID > 700000000) & (ID < 800000000)) | ((ID > 804650000) & (ID < 804685000))
g1[g2] = False
g3 = (age == 24) & ~g1 & ~g2
g4 = (ID > 900000000) & (age >= 50) & ~g1
subgroup = np.zeros((len(ID),5), bool)
subgroup[g1, 0] = True
subgroup[g2, 1] = True
subgroup[g3, 2] = True
subgroup[g4, 3] = True
subgroup[np.sum(subgroup[:, :-1], 1) == 0, 4] = True
co = ['g', 'r', 'k', 'c', 'b']
label = ['linear', 'random age', 'age 24', 'random ID', 'all the rest']
lbl = []
for jj in range(len(co)):
    lbl.append(f"{label[jj]} ({str(np.sum(subgroup[okay, jj]))})")
##
plt.figure()
for ii in range(len(millions)):
    ifrom = millions[ii]*10**8
    ito = (millions[ii]+1)*10**8
    plt.subplot(2, 2, ii+1)
    group = okay & (ID >= ifrom) & (ID < ito)
    # plt.plot(df['ID'][group], df['age'][group], '.'+'b')
    if ii == 0:
        for jj in range(len(co)):
            plt.plot(-5, -5, '.' + co[jj])
        plt.legend(lbl)
    for jj in range(len(co)):
        plt.plot(df['ID'][group & subgroup[:, jj]], age[group & subgroup[:, jj]], '.'+co[jj])
    x = [ifrom, ifrom+50000000, ito]
    xst = [str(x) for x in x]
    plt.xticks(x, xst)
    plt.xlim(ifrom, ito)
    plt.text(ifrom+50000000, 95,  f'ID from {ifrom} to {ito}', ha='center')
    plt.ylabel('age')
    plt.xlabel('ID')
    plt.ylim(0, 105)
    plt.grid()
plt.suptitle('ID numbers against age for deaths reported by Gaza MoH\n'
             'Of 21323 reported deaths there were 17855 unique and valid IDs and age')

