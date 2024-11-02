"""Read manually exported telegram data from json, and saves csv."""
import pandas as pd
# import os
import numpy as np
# import sys
import json
from glob import glob
# sys.path.append('code')
# df = pd.read_json('/home/innereye/Downloads/Telegram Desktop/ChatExport_2024-10-18/result.json')

data_dir = '/home/innereye/Downloads/Telegram Desktop/'
data_dir = sorted(glob(data_dir+'ChatExport*'))[-1]
file = glob(data_dir+'/*.json')[0]
f = open(file)
data = json.load(f)
f.close()
# df = pd.DataFrame(columns=['date', 'text'])
# for ii in range(len(data['messages'])):
#     date = data['messages'][ii]['date'].replace('T', ' ')
#     text = data['messages'][ii]['text']
#     df.at[ii, 'date'] = date
#     df.at[ii, 'text'] = text
#     print(ii)
# df = df[df['date'] > '2023-10-07']
# df.to_excel('~/Documents/tsahal.xlsx')


messages = []
for message in data['messages']:
    if 'date' in message and 'text' in message:
        # Handle both cases where 'text' is a string or a list (in case of formatting markers)
        if isinstance(message['text'], list):
            text = ''.join([str(item) if isinstance(item, str) else '' for item in message['text']])
        else:
            text = message['text']
        text = text.replace('דובר צה״ל:', '').replace('דובר צה"ל:', '').strip()
        messages.append({
            'date': message['date'].replace('T', ' '),
            'text': text
        })

# Create a DataFrame and export it to Excel
df0 = pd.read_csv('data/idf_telegram_oct23.csv')
df1 = pd.DataFrame(messages)
last = np.where(df1['date'].values == df0['date'].values[-1])[0]
if len(last) != 1:
    raise ValueError(f"expected to find one instance of {df0['date'].values[-1]} in date list")
df_extra = df1[last[0]+1:]
# df1 = df1[df1['date'] > '2023-10-07']
df = pd.concat([df0, df_extra], ignore_index=True)
df.to_csv('data/idf_telegram_oct23.csv', index=False)
fa = df1[df1['text'].str.contains('שווא')]
fa.to_csv('~/Documents/fa.csv', index=False)
##
fa = pd.read_csv('~/Documents/fa.csv')
alarms = pd.read_csv('data/alarms.csv')
ii = len(fa)-1
text = fa['text'][ii]
date = fa['date'][ii]
until = np.where(alarms['time'] < date)[0][-1]

for ii in range(len(fa)):
    text = fa['text'][ii]
    date = fa['date'][ii]
    until = np.where(alarms['time'] < date)[0][-1]
    if alarms['origin'][until] == 'FA':
        print('knew it')
    else:
        print(f"missed {ii}")
