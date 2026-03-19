import os
import pandas as pd
import numpy as np


url = 'https://raw.githubusercontent.com/dleshem/israel-alerts-data/main/israel-alerts.csv'
# response = requests.get(url)
# response.raise_for_status()  # Raise an exception for HTTP errors
# csv_content = response.content.decode('utf-8')
df = pd.read_csv(url)
# Filter for category 14 events
df14 = df[df['category'] == 14].copy()
# Convert 'alertDate' to datetime objects
df14['date_orig'] = df14['date']
df14['time_orig'] = df14['time']
df14['datetime'] = pd.to_datetime(df14['date'] + ' ' + df14['time'], dayfirst=True)
df14['date'] = pd.to_datetime(df14['date'], dayfirst=True)
# Filter for dates from Feb 28 2026 onwards
start_date = pd.to_datetime('2026-02-28')
df14 = df14[df14['date'] >= start_date]
df14 = df14[df14['category_desc'].str.contains('בדקות הקרובות')]
df14 = df14.reset_index(drop=True)
datetimes = np.unique(df14['datetime'])
#find differences larger than 60sec in datetimes
difs = [0] + [int(i)+1 for i in np.where(np.diff(datetimes) > np.timedelta64(10, 'm'))[0]]
dfc = pd.DataFrame(columns=['rid', 'date', 'from_time', 'to_time', 'n locations'])
for idt in range(len(difs)):
    start_idx = difs[idt]
    if idt == len(difs)-1:
        end_idx = len(datetimes)
    else:
        end_idx = difs[idt + 1]
    locations = []
    for jdt in range(start_idx, end_idx):
        locations.extend(list(df14['data'][df14['datetime'] == datetimes[jdt]]))
    row = len(dfc)
    dfc.at[row, 'rid'] = ';'.join(list(df14['rid'][start_idx:end_idx].values.astype(str)))
    dt = datetimes[start_idx]
    dfc.at[row, 'date'] = str(np.datetime_as_string(dt, unit='D'))
    dfc.at[row, 'from_time'] = str(np.datetime_as_string(dt)).split('T')[1].split('.')[0]
    dfc.at[row, 'to_time'] = str(np.datetime_as_string(datetimes[end_idx-1])).split('T')[1].split('.')[0]

    dfc.at[row, 'n locations'] = len(np.unique(locations))
    dfc.at[row, 'locations'] = ';'.join(list(np.unique(locations)))
    # if len(locations) != len(np.unique(locations)):
    #     print(dt)
print(dfc)
dfc.to_csv('~/Documents/iac.tsv', index=False, sep='\t')

dfc_cleaned = dfc[dfc['n locations'] > 50]
import plotly.graph_objects as go
medians = dfc_cleaned.groupby('date')['n locations'].median().reset_index()
fig = go.Figure()
fig.add_trace(go.Scatter(x=dfc['date'], y=dfc['n locations'], mode='markers', name='Data'))
fig.add_trace(go.Bar(x=medians['date'], y=medians['n locations'], marker=dict(color='black'), name='Median'))
fig.update_layout(
    xaxis=dict(tickangle=90, dtick="D1"),
    title={
        'text': "מספר מיקומים להתרעה, לפי יום",
        'x': 0.5,
        'xanchor': 'center'
    },
    yaxis_title="מספר המקומות"
)
fig.write_html(os.environ['HOME'] + '/Documents/inadvance_locations.html')

## look for alarms from Iran not preceded by warning
dfc = pd.read_csv('~/Documents/iac.tsv', sep='\t')
dfa = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
dfa = dfa[dfa['time'] > '2026-02-28']
dfa = dfa[dfa['origin'] == 'Iran']
dfa = dfa[dfa['threat'] == 0]
dfa.reset_index(drop=True, inplace=True)
timec = pd.to_datetime(dfc['date'] + ' ' + dfc['from_time'])
timea = pd.to_datetime(dfa['time'])
for iw in range(len(dfc)):
    # find the id of the next alarm in dfa that has origin Iran
    inext = np.where((timea > timec[iw]) & (timea - timec[iw] < np.timedelta64(10, 'm')))[0]
    if len(inext) == 0:
        print('no alarm after warning?')
        continue
    else:
        # inext = inext[0]
        if timea[inext[0]] - timec[iw] > np.timedelta64(25, 'm'):
            print('too long wait')
        else:
            id = np.unique(dfa['id'].values[inext])
            dfc.at[iw, 'tzofar id'] = ';'.join(id.astype(str))
            # look for missing spots
            loca = []
            for d in id:
                loca.extend(dfa['cities'][dfa['id'] == d].values)
            loca = np.unique(loca)
            missing = []
            for loc in loca:
                if loc not in dfc['locations'][iw] and dfc['locations'][iw] != 'ברחבי הארץ':
                    missing.append(loc)
            print(len(missing),'/',len(loca))
            dfc.at[iw, 'missing'] = ';'.join(missing)
dfc.to_csv('~/Documents/iac.tsv', index=False, sep='\t')


# missed = np.zeros(len(dfa), int)
# last_warning = []
# for ii in range(len(missed)):
#     dfc_before = dfc[(timec < timea[ii]) & (timec > timea[ii] - np.timedelta64(15, 'm'))]
#     last_warning.append('')
#     if dfc_before['locations'].str.contains('ברחבי הארץ').any():
#         continue
#     if dfc_before['locations'].str.contains(dfa['cities'][ii]).any():
#         continue
#     if len(dfc_before) == 0:
#         last_warning[-1] = 'no warning'
#         missed[ii] = -1
#     else:
#         last_warning[-1] = dfc_before['date'].values[-1] + ' ' + dfc_before['to_time'].values[-1]
#         missed[ii] = dfc_before.index[-1]
#     print(f'{ii}/{len(missed)}', end='\r')
#
# np.sum(missed > 0)
# dates = np.unique(dfc['date'])
# sum_missed = []
# for idate in range(2, len(dates) - 1):
#     date = dates[idate]
#     idxa = (dfa['time'].values > date) & (dfa['time'].values < dates[idate + 1]) & (missed > 0)
#     sum_missed.append(np.sum(idxa))
# fig = go.Figure()
# fig.add_trace(go.Bar(x=dates[2:-1], y=sum_missed, marker=dict(color='black'), name='Sum'))
# fig.update_layout(
#     xaxis=dict(tickangle=90, dtick="D1"),
#     title={
#         'text': "התרעה מקדימה - מספר החטאות ליום",
#         'x': 0.5,
#         'xanchor': 'center'
#     },
#     yaxis_title="מספר המקומות"
# )
# # missed = np.zeros(len(dfa), int)
# last_warning = []
# for ii in range(len(missed)):
#     dfc_before = dfc[(timec < timea[ii]) & (timec > timea[ii] - np.timedelta64(15, 'm'))]
#     last_warning.append('')
#     if dfc_before['locations'].str.contains('ברחבי הארץ').any():
#         continue
#     if dfc_before['locations'].str.contains(dfa['cities'][ii]).any():
#         continue
#     if len(dfc_before) == 0:
#         last_warning[-1] = 'no warning'
#         missed[ii] = -1
#     else:
#         last_warning[-1] = dfc_before['date'].values[-1] + ' ' + dfc_before['to_time'].values[-1]
#         missed[ii] = dfc_before.index[-1]
#     print(f'{ii}/{len(missed)}', end='\r')
#
# np.sum(missed > 0)
# dates = np.unique(dfc['date'])
# sum_missed = []
# for idate in range(2, len(dates) - 1):
#     date = dates[idate]
#     idxa = (dfa['time'].values > date) & (dfa['time'].values < dates[idate + 1]) & (missed > 0)
#     sum_missed.append(np.sum(idxa))
# fig = go.Figure()
# fig.add_trace(go.Bar(x=dates[2:-1], y=sum_missed, marker=dict(color='black'), name='Sum'))
# fig.update_layout(
#     xaxis=dict(tickangle=90, dtick="D1"),
#     title={
#         'text': "התרעה מקדימה - מספר החטאות ליום",
#         'x': 0.5,
#         'xanchor': 'center'
#     },
#     yaxis_title="מספר המקומות"
# )
# fig.write_html(os.environ['HOME'] + '/Documents/count_missing.html')





