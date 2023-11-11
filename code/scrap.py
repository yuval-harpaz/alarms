import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

# https://he.wikipedia.org/wiki/%D7%94%D7%9C%D7%97%D7%99%D7%9E%D7%94_%D7%91%D7%A8%D7%A6%D7%95%D7%A2%D7%AA_%D7%A2%D7%96%D7%94_%D7%9C%D7%90%D7%97%D7%A8_%D7%9E%D7%91%D7%A6%D7%A2_%D7%A9%D7%95%D7%9E%D7%A8_%D7%94%D7%97%D7%95%D7%9E%D7%95%D7%AA

os.chdir('/home/innereye/alarms/data/')
dfwar = pd.read_csv('alarms.csv')

# last_alarm = pd.to_datetime(dfwar['time'][len(dfwar)-1])
# last_alarm = last_alarm.tz_localize('Israel')
dfwar = dfwar[dfwar['threat'] == 0]
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
gaza = dfwar[dfwar['origin'] == 'Gaza']
gaza = dfwar.reset_index(drop=True)
lebanon = dfwar[dfwar['origin'] == 'Lebanon']
lebanon = dfwar.reset_index(drop=True)




loc = np.unique(dfwar['cities'])
n = np.zeros(len(loc), int)
for ii in range(len(loc)):
    n[ii] = np.sum(dfwar['cities'] == loc[ii])

nn = 30
tick = np.array([x[::-1] for x in loc])
order = np.argsort(-n)
##
plt.figure()
plt.bar(range(1, nn+1), n[order[:nn]])
for ii in range(nn):
    plt.text(ii+1-0.1, 5, tick[order[ii]], rotation=90, color='w')
    plt.text(ii+1-0.2, n[order[ii]] + 3, n[order[ii]], color = 'k')
ax = plt.gca()
ax.yaxis.grid()
plt.xticks([])
plt.title('rocket alarms from 2023-10-7 until ' + dfwar['time'][len(dfwar)-1])


## יזכור
# https://www.izkor.gov.il/search/predefined/%D7%9B%D7%9C%20%D7%97%D7%9C%D7%9C%D7%99%20%D7%9E%D7%A2%D7%A8%D7%9B%D7%95%D7%AA%20%D7%99%D7%A9%D7%A8%D7%90%D7%9C/0/25/d
# https://www.izkor.gov.il/searchforMemoryCandle/extended-search?death_date=2016&death_date_to=2016
# https://fs.knesset.gov.il/globaldocs/MMM/9107116b-1c0e-e711-80cc-00155d0206a2/2_9107116b-1c0e-e711-80cc-00155d0206a2_11_8715.pdf
# https://raw.githubusercontent.com/50stuck/Izkor-Git/763fe7f303e9d948d0b096033ed0e763742f4aea/HalalDataFull_April15.csv
# year = requests.get('https://www.izkor.gov.il/searchforMemoryCandle/extended-search?death_date=2016&death_date_to=2016')
mako = pd.read_excel('/home/innereye/Documents/mako.xlsx')
df = pd.read_csv('data/deaths_by_year.csv')

df = df[44:]
year = df['year'].values
armed = df['armed_forces'].values
civil = df['civilians'].values
war = mako['g'].to_numpy()
war = np.array([x for x in war if type(x) == str])
war_armed = np.sum((war == 'חייל') | (war == 'שוטר') | (war == 'צה"ל') | (war == 'שב"כ'))
civil[-1] += len(war)-war_armed
armed[-1] += war_armed
select = [1948, 1956, 1967, 1973, 1982, 2002, 2023]
##
plt.figure()
plt.subplot(2,1,1)
plt.bar(year, civil)
ax = plt.gca()
ax.yaxis.grid()
plt.title('civilians   ' + 'אזרחים'[::-1])
plt.xticks(select, select, rotation=30)
for ii in range(len(select)):
    n = int(civil[year == select[ii]][0])
    plt.text(select[ii], n + 10, str(n), ha='center')
plt.subplot(2, 1, 2)
plt.bar(year, armed)
plt.xticks(select, select, rotation=30)
ax = plt.gca()
ax.yaxis.grid()
plt.title('armed forces  ' + 'כוחות הביטחון'[::-1])
for ii in range(len(select)):
    n = armed[year == select[ii]][0]
    plt.text(select[ii], n + 10, str(n), ha='center')
## pie
mako['g'] == 'אזרח'

