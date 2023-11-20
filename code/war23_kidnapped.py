import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

with open('מלחמה בישראל_ שמות החטופים שפורסמו - חדשות - הארץ.html') as f:
    lines = f.readlines()

## data
data = []
for ii in range(len(lines)):

    if 'war-kidnapped-card__name' in lines[ii]:
        # print(ii)
        new = False
        try:
            if ',' in lines[ii]:
                name = lines[ii][lines[ii].index('>')+1:lines[ii].index(',')]
            else:
                name = lines[ii][lines[ii].index('>') + 1:lines[ii].index('/')-1]
            print(name)
            age = ''
            story = ''
            fro = ''
            new = True
        except:
            print('FAILED name: ' + lines[ii][:100])
        if new:
            if ',' in lines[ii]:
                try:
                    age = lines[ii][lines[ii].index(',')+2:lines[ii].index('/')-1]
                    print(age)
                except:
                    print('FAILED age: ' + lines[ii][:100])
        if new:
            for jj in range(ii, ii+10):
                if 'war-kidnapped-card__details' in lines[jj]:
                    fro = lines[jj][lines[jj].index('>') + 1:lines[jj].index('/') - 1]
                elif not '<' in lines[jj] and len(lines[jj].replace(' ', '')) > 1:
                    story = lines[jj]
        if new:
            data.append([name, age, fro, story])
df = pd.DataFrame(data, columns=['name','age','from','story'])
df['story'] = df['story'].str.strip()
df.to_csv('kidnapped.csv', index=False)
'''
</div>
<div class="war-kidnapped-card__content">
    <h3 class="war-kidnapped-card__name">אוריאל ברוך, 35</h3>
    
    <h3 class="war-kidnapped-card__details">גבעון</h3>
    
    
    <p class="war-kidnapped-card__text">
        
        נחטף מהמסיבה ברעים    
    </p>
</div>
'''
##
df = pd.read_csv('kidnapped.csv')
with open('239 חטופים_ השמות, הפנים, הסיפורים.html') as f:
    txt = f.read()

lines = txt.split('</span></span></div></h3>')

lines = txt.split('style="font-weight:bold">')
for ii in range(len(lines)):
    line = lines[ii].replace('<span data-text="true">','')
    line = line[:line.index('<')]
    print(line)

for ii in range(len(df)):
    if type(df['story'][ii]) == str and 'מסיבה' in df['story'][ii]:
        df.at[ii, 'circum'] = 'party'
    elif df['status'][ii] == 'חייל':
        df.at[ii, 'circum'] = 'army'
    else:
        df.at[ii, 'circum'] = 'home/work'

labels = ['home | work', 'party', 'army']
x = []
for ii in range(3):
    x.append(np.sum(df['circum'].values == labels[ii]))

for il in range(len(labels)):
    labels[il] = labels[il]+': '+str(x[il])

colors = ['b', 'orange', 'g']
plt.figure()
plt.pie(x, labels=labels, colors=colors)

dfd = pd.read_csv('../alarms/data/deaths_manual.csv')



x1 = []
for story in  dfd['story'].values:
    if type(story) == str:
        x1.append('מסיבה' in story)
x1 = np.sum(x1)
x0 = np.sum(dfd['status'] == 'אזרח') - x1
x2 = np.sum(dfd['status'] == 'שוטר') + np.sum(dfd['status'] == 'חייל')
xx = [x0, x1, x2]

# for ii in range(3):
#     x.append(np.sum(df['circum'].values == labels[ii]))
labels1 = ['home | work', 'party', 'army | police']
for il in range(len(labels)):
    labels1[il] = labels1[il]+': '+str(xx[il])

startangle=90
colors = ['b', 'orange', 'g']
plt.figure()
plt.subplot(1,2,1)
plt.pie(x, labels=labels, colors=colors, startangle=startangle)
plt.title('kidnapped ('+str(np.sum(x))+')')
plt.subplot(1,2,2)
plt.pie(xx, labels=labels1, colors=colors, startangle=startangle)
plt.title('deaths ('+str(np.sum(xx))+')')


ages = np.array([float(x.replace('9 חודשים', '999')) for x in df['age'].values if type(x) == str])
ages[ages == 999] = 0
edges = np.arange(0, 101,5)-0.5
tick = edges+0.5

agesd = dfd['age'][dfd['status'] == 'אזרח'].values.astype(float)
agesd = agesd[agesd > 0]

plt.figure()
plt.subplot(1, 2, 1)
plt.bar(edges[:-1] + 2.5, np.histogram(ages, edges)[0], 4)
plt.xticks(edges, tick.astype(int))
plt.title('kidnapped age distribution')
ax = plt.gca()
ax.yaxis.grid('on')
plt.ylabel('count')
plt.xlabel('age')
plt.subplot(1, 2, 2)
plt.bar(edges[:-1] + 2.5, np.histogram(agesd, edges)[0], 4)
plt.xticks(edges, tick.astype(int))
plt.title('civilian deaths age distribution')
ax = plt.gca()
ax.yaxis.grid('on')
plt.ylabel('count')
plt.xlabel('age')
plt.yticks(range(0, 160, 10))
# with open('239.html') as f:
#     txt = f.read()
# lines = txt.split('.')
#
# a = 0
# for ii in range(len(lines)):
#     line = lines[ii].split(',')
#     name = line[0].split('בן')[0].split('בת')[0].strip()
#     if name in df['name'].values:
#         a += 1
#     else:
#         print(name)
#
# local = '/home/innereye/alarms/'
# islocal = False
# if os.path.isdir(local):
#     os.chdir(local)
#     islocal = True
#     sys.path.append(local + 'code')
#
# df = pd.read_csv('data/deaths_manual.csv')
#
# status = df['status'].values
# rank = df['rank'].values.astype(str)
# statusu = np.unique(status)
# for ii in range(len(status)):
#     if status[ii] == 'חייל':
#         if 'מיל' in rank[ii]:
#             status[ii] = 'מילואים'
#         elif rank[ii] in [ 'אל"ם', 'סא"ל', 'סג"ם', 'סגן', 'סרן', 'רס"ן']:
#             status[ii] = 'קצין'
#     if ' זר' in status[ii] or status[ii] == 'סטודנט':
#         status[ii] = 'זר'
# statusu = np.unique(status)
#
# stat = ['אזרח', 'כבאי', 'שוטר', 'מילואים', 'חייל', 'קצין', 'שב"כ', 'זר']
# colors = ['b', 'r','cyan','olive','green',(0, 1, 0),'brown','orange']
# x = np.zeros(len(stat), int)
# for jj in range(len(stat)):
#     x[jj] = np.sum(status == stat[jj])
#
# labels = [ll[::-1] for ll in stat]
# for il in range(len(labels)):
#     labels[il] = str(x[il]) + ' :' + labels[il]
# plt.pie(x, labels=labels, colors=colors)
#
# state = ['civilian', 'fire-fighter', 'police', 'reserves', 'soldier', 'officer', 'Shin-Bet', 'foreign']
# for il in range(len(labels)):
#     labels[il] = state[il]+': '+str(x[il])
# plt.pie(x, labels=labels, colors=colors)
