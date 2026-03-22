import pandas as pd
import numpy as np   
import os
import requests
import time
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import json
# import json from ~/RedAlert/telegram.json
with open(os.environ['HOME'] + '/RedAlert/telegram.json', 'r') as f:
    txt = f.read()
    tele = json.loads(txt)
messages = tele['messages']


# sometimes the message['text'] list starts with ['🚨 ', '✈ ', '🔓 '
## make a list of messages
# look for אזור in the list, take the locations after every instance.
# when no אזור is found, make sure it is ברחבי הארץ. this can be no-travel news flash, or update saying out of shelter but stay near
# find message type by presence of : but without https:// when no : is present this should be newsflash בדקות הקרובות
dfm = pd.DataFrame(columns=['message id', 'message time', 'time in message', 'type', 'message', 'locations'])
for ii in range(len(messages)):
    message = ''
    time_in_message = ''
    message_type = ''
    timestamp = messages[ii]['date'].replace('T', ' ')
    # find time and type
    tim = [p['text'] for p in messages[ii]['text'] if type(p) == dict and ':' in p['text'] and '://' not in p['text']]
    if len(tim) == 0:
        badakot = [p['text'] for p in messages[ii]['text'] if type(p) == dict and 'בדקות הקרובות' in p['text']]
        if len(badakot) > 0:
            message_type = 'מבזק'
            message = badakot[0]
            time_in_message = ''
        else:
            message = ''
            time_in_message = ''
            message_type = ''
    elif len(tim) == 1:
        time_in_message = tim[0].split(')')[-1].strip()
        # if time_in_message not in timestamp:
        #     print(timestamp+' '+time_in_message)
        message_type = tim[0].split('(')[0].strip()
        message = [m['text'] for m in messages[ii]['text'] if type(m) == dict and len(m['text']) > 0][-1]
        if 'אזור ' in message:
            for start_looking in range(len(messages[ii]['text'])):
                if type(messages[ii]['text'][start_looking]) == dict and time_in_message in messages[ii]['text'][start_looking]['text']:
                    start_looking += 1
                    break
            for jj in range(start_looking, len(messages[ii]['text'])):
                if type(messages[ii]['text'][jj]) == dict:
                    message = messages[ii]['text'][jj]['text']
                    break
            # print('bad message: '+message)
    iregion = []
    for jj in range(len(messages[ii]['text'])):
        if type(messages[ii]['text'][jj]) == dict and 'אזור ' in messages[ii]['text'][jj]['text']:
            iregion.append(jj)
    locations = []
    for jj in iregion:
        # if messages[ii]['id'] == 22533:
        #     print('debug')
        locations.append(messages[ii]['text'][jj+1].replace('(', '').strip())
    if len(locations) > 0:
        locations = ', '.join(locations)
    else:
        if 'ברחבי הארץ' in messages[ii]['text'][-1]:
            locations = 'ברחבי הארץ'
        else:
            locations = ''
    locations = locations.replace(', ', '; ')
    if message_type == '':
        if 'ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו' in messages[ii]['text'][0]['text']:
            message_type = 'עדכון'
            message = 'ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו'
        elif 'האירוע הסתיים' in messages[ii]['text'][0]['text']:
            message_type = 'עדכון'
            message = 'האירוע הסתיים'
        elif 'סיום שהייה בסמיכות למרחב המוגן' in messages[ii]['text'][0]['text']:
            message_type = 'עדכון'
            message = 'סיום שהייה בסמיכות למרחב המוגן'
        else:
            print('bad type')
    elif 'http' in message:
        message_type = 'חדירת מחבלים'
        message = locations.split('\n')[2]
        locations = locations.split('\n')[0]
    dfm.loc[len(dfm)] = [messages[ii]['id'], timestamp, time_in_message, message_type, message, locations]
dfm.to_excel('~/RedAlert/telegram_messages.xlsx', index=False, sheet_name='data')

## find times missing from alarms.csv
dfm = pd.read_excel('~/RedAlert/telegram_messages.xlsx', sheet_name='data')
rnd = dfm[dfm['type'].isin(['חדירת כלי טיס עוין', 'ירי רקטות וטילים'])]
rnd = rnd.reset_index(drop=True)
timet = pd.to_datetime(rnd['message time']).values
dfa = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
dfa = dfa[dfa['time'] > '2026-02-28']
timea = pd.to_datetime(dfa['time']).values
issues = pd.DataFrame(columns=['message id', 'message time', 'type', 'closest', 'locations'])
for ii in range(len(timet)):
    if timet[ii] not in timea:
        closest = np.min(np.abs(timea - timet[ii]))
        if closest > np.timedelta64(9, 's'):
            issues.loc[len(issues)] = [rnd['message id'][ii], rnd['message time'][ii], rnd['type'][ii], str(closest.astype('timedelta64[s]')).replace(' seconds', ''), rnd['locations'][ii]]
issues.to_excel('~/RedAlert/issues.xlsx', index=False, sheet_name='data')

## make sure misses are real
# Load issues and validate them
issues_loaded = pd.read_excel('~/RedAlert/issues.xlsx', sheet_name='data')
rnd_with_time = rnd.copy()
rnd_with_time['datetime'] = pd.to_datetime(rnd_with_time['message time'])
dfa_with_time = dfa.copy()
dfa_with_time['datetime'] = pd.to_datetime(dfa_with_time['time'])

print("\n=== Validating Issues ===")
for idx, row in issues_loaded.iterrows():
    message_id = row['message id']
    message_time = pd.to_datetime(row['message time'])
    issue_type = row['type']
    locations_str = str(row['locations'])
    
    # Extract one location (take the first one if multiple)
    locations_list = [loc.strip() for loc in locations_str.split(';') if loc.strip()]
    example_location = locations_list[0] if locations_list else ''
    
    # Find previous occurrence in dfa before message time
    prev_in_dfa = dfa_with_time[dfa_with_time['datetime'] < message_time].sort_values('datetime', ascending=False)
    prev_match = None
    if len(prev_in_dfa) > 0:
        prev_match = prev_in_dfa.iloc[0]
    
    # Find next occurrence in dfa after message time
    next_in_dfa = dfa_with_time[dfa_with_time['datetime'] >= message_time].sort_values('datetime', ascending=True)
    next_match = None
    if len(next_in_dfa) > 0:
        next_match = next_in_dfa.iloc[0]
    
    # Check if previous match has a corresponding event in rnd with similar time
    prev_rnd_match = False
    if prev_match is not None:
        prev_dfa_time = pd.to_datetime(prev_match['time'])
        # Find events in rnd with similar time to prev_match
        time_diffs = np.abs(rnd_with_time['datetime'] - prev_dfa_time)
        if np.min(time_diffs) < np.timedelta64(10, 's'):  # within 10 seconds
            prev_rnd_match = True

    # Check if next match has a corresponding event in rnd with similar time
    next_rnd_match = False
    if next_match is not None:
        next_dfa_time = pd.to_datetime(next_match['time'])
        # Find events in rnd with similar time to next_match
        time_diffs = np.abs(rnd_with_time['datetime'] - next_dfa_time)
        if np.min(time_diffs) < np.timedelta64(10, 's'):  # within 10 seconds
            next_rnd_match = True

    # Determine which neighboring events were found in rnd
    neighbors_found = []
    if prev_rnd_match:
        neighbors_found.append('PREV')
    if next_rnd_match:
        neighbors_found.append('NEXT')
    neighbors_str = ', '.join(neighbors_found) if neighbors_found else 'NONE'
    
    # If both neighbors are found, this confirms the issue is real
    confirmed = 'CONFIRMED' if (prev_rnd_match and next_rnd_match) else 'NOT_CONFIRMED'
    if confirmed == 'NOT_CONFIRMED':
        print(f"Message ID: {message_id} | Location: {example_location} | Neighbors: {neighbors_str} | {confirmed}")
        issues_loaded.at[idx, 'confirmed'] = '?'
    else:
        issues_loaded.at[idx, 'confirmed'] = 'confirmed'
issues_loaded.to_excel('~/RedAlert/issues_validated.xlsx', index=False, sheet_name='data')


# # explore mmessages
# types = []
# for ii in range(len(messages)):
#     tim = [p['text'] for p in messages[ii]['text'] if type(p) == dict and ':' in p['text'] and '://' not in p['text']]
#     if len(tim) == 1:
#         print(ii)
#         print(messages[ii]['text'])
#
#     ezor = [p['text'] for p in messages[ii]['text'] if type(p) == dict and 'אזור' in p['text']]
#     if len(ezor) == 0:
#         print(ii)
#         print(messages[ii]['text'])
#
#
#     prts = [p for p in messages[ii]['text'] if type(p) == str and '(' in p]
#     if len(prts) == 1:
#         print(ii)
#         # print(f'{ii} : {prts[0][1:-2]}')
#     if len(messages[ii]['text'][-1]) == 0:
#         print(ii)
#     timestamp = messages[ii]['date']
#     if messages[ii]['text'][0] in ['🚨 ', '✈ ', '🔓 ']:
#         pass # print(messages[ii]['text'][1])
#     else:
#         print(str(ii) + ' : ' + str(messages[ii]['text']))


#     if messages[ii]['text'][0] in ['🚨 ', '✈ ', '🔓 ']:
#         pass # print(messages[ii]['text'][1])
#     else:
#         print(str(ii) + ' : ' + str(messages[ii]['text']))
#
# message = 26817
# imessage = [i for i in range(len(messages)) if messages[i]['id'] == message]
# if len(imessage) == 1:
#     imessage = imessage[0]
# else:
#     raise Exception('expected one ' + str(message))
# locations = messages[imessage]['text']

# key = os.environ['RedAlert']
# start = datetime.strptime('2026-02-28', '%Y-%m-%d')
# end = datetime.now()
# dates = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range((end-start).days + 1)]
# sp = 0
# plt.figure()
# for typ in ['missiles', 'newsFlash']:
#     stats = pd.DataFrame(columns=['date','min diff', 'n events'])
#     for date in dates:
#         url = f"https://redalert.orielhaim.com/api/stats/history?category={typ}&startDate={date}T00:00:00Z&endDate={date}T23:59:59Z&sort=timestamp&order=asc&limit=100"
#         headers = {"Authorization": f"Bearer {key}"}
#         response = requests.get(url, headers=headers)
#         data = response.json()
#         dfr = pd.DataFrame(data['data'])
#         row = len(stats)
#         stats.at[row, 'date'] = date
#         if len(dfr) == 0:
#             stats.at[row, 'min diff'] = 0
#             stats.at[row, 'n events'] = 0
#         else:
#             dfr['datetime'] = pd.to_datetime(dfr['timestamp'])
#             np.sort(dfr['datetime'].diff())
#             diffs = dfr['datetime'].diff().values[1:]
#             seconds = np.sort(diffs).astype('timedelta64[s]').astype(int)
#             stats.at[row, 'min diff'] = seconds[0]
#             stats.at[row, 'n events'] = len(dfr)
#     for measure in ['min diff', 'n events']:
#         sp += 1
#         plt.subplot(2, 2, sp)
#         plt.bar(range(len(stats)), stats[measure])
#         plt.xticks(range(len(stats)), stats['date'], rotation=30, ha='right')
#         plt.xlim(-0.5, len(dates))
#         plt.gca().yaxis.grid()
#         plt.title(f"{typ} {measure}")
#         for jj in range(len(stats)):
#             plt.text(jj, stats[measure][jj], str(stats[measure][jj]), ha='center')
#
# ##  matchin redalert to alarms.csv. did not finish because moed on to take ground truth from telegram
# dfa = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
# dfa = dfa[dfa['time'] > '2026-02-28']
# dfa = dfa[dfa['threat'] == 0]
# dfa.reset_index(drop=True, inplace=True)
# # timec = pd.to_datetime(dfc['date'] + ' ' + dfc['from_time'])
# timea = pd.to_datetime(dfa['time'])
# typ = 'missiles'
# for date in dates:
#     url = f"https://redalert.orielhaim.com/api/stats/history?category={typ}&startDate={date}T00:00:00Z&endDate={date}T23:59:59Z&sort=timestamp&order=asc&limit=100"
#     headers = {"Authorization": f"Bearer {key}"}
#     response = requests.get(url, headers=headers)
#     data = response.json()
#     dfr = pd.DataFrame(data['data'])
#     row = len(stats)
#     # stats.at[row, 'date'] = date
#     if len(dfr) == 0:
#         dfr['datetime'] = pd.to_datetime(dfr['timestamp'])
#         for ievent in range(len(dfr)):
#             event_time = dfr['datetime'][ievent]
#             for loc in dfr['cities'][ievent]:
#                 name = loc['name']
#                 rowa = np.where((dfa['cities'].values == name) and (np.abs(timea - event_time) < np.timedelta64(2, 'm')))[0]
#
# # key = os.environ['RedAlert']
# # command = f'curl "https://redalert.orielhaim.com/api/stats/history?category=missiles&startDate=2026-03-14T00:00:00Z&endDate=2026-03-14T23:59:59Z&sort=timestamp&order=asc&limit=100"   -H "Authorization: Bearer {key}" -o ~/Documents/today.json'
# # os.system(command)