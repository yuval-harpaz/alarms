import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
try:
    local = '/home/innereye/alarms/'
    islocal = False
    if os.path.isdir(local):
        os.chdir(local)
        islocal = True
    dfwar = pd.read_csv('data/alarms.csv')
    dfwar = dfwar[dfwar['threat'] == 0]
    dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
    dfleb = dfwar[dfwar['origin']  == 'Lebanon']
    dfleb = dfleb.reset_index(drop=True)
    dateleb = np.array([d[:10] for d in dfleb['time']])
    dfwar = dfwar[dfwar['origin']  == 'Gaza']
    dfwar = dfwar.reset_index(drop=True)
    daterange = pd.date_range(start='2023-10-07', end=datetime.today().strftime('%Y-%m-%d'), freq='D')
    date = np.array([d[:10] for d in dfwar['time']])
    dateu = np.unique(daterange)
    dateu = np.array([str(x)[:10] for x in dateu])
    datex = list(dateu[1::7])
    events = {'2023-10-27': 'ground assault', '2023-11-03': "Nasrallah's speach", '2023-11-24': 'ceasefire'}
    date_event = list(events.keys())
    datex += date_event
    datex = np.unique(datex)
    ticks = list(datex)
    for ii in range(len(date_event)):
        d = date_event[ii]
        ticks[int(np.where(datex == d)[0])] = events[d]
    # coo = pd.read_csv('data/coord.csv')
    coo = pd.read_csv('data/coord_km_gaza.csv')
    edges = [0, 7, 15, 30, 50, 300]
    n_lines = len(edges)
    hist = np.zeros((len(edges), len(dateu)))
    for day in range(len(dateu)):
        idx = date == dateu[day]
        ids = np.unique(dfwar['time'][idx])
        dist = np.zeros(len(ids))
        for iid in range(len(ids)):
            rows = np.where(dfwar['time'] == ids[iid])[0]
            lat = np.zeros(len(rows))
            long = np.zeros(len(rows))
            d = []
            for irow, row in enumerate(rows):
                d.append(coo['km_from_Gaza'][coo['loc'] == dfwar['cities'].values[row]].values[0])
            dist[iid] = np.mean(d)
        hist[:-1, day] = np.histogram(dist, edges)[0]
        idxleb = dateleb == dateu[day]
        idsleb = np.unique(dfleb['time'][idxleb])
        hist[-1, day] = len(idsleb)
    ##
    df = pd.DataFrame(dateu, columns=['date'])
    for irange in range(len(edges) - 1):
        df[(str(edges[irange])+'-'+str(edges[irange+1])).replace('-300', '+')] = hist[irange, :]
    df['Lebanon'] = hist[-1, :]
    ##
    now = np.datetime64('now', 'ns')
    now = np.datetime64('now', 'ns')
    nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
    nowstr = str(nowisr)[:16].replace('T', ' ')
    tail_html = f'''
                Lines represent 7-day moving average (±3 days)
                By <a href="https://twitter.com/yuvharpaz" target="_blank">@yuvharpaz</a>. Data from <a href="https://www.oref.org.il" target="_blank">THE NATIONAL EMERGENCY PORTAL</a>
                 via <a href="https://www.tzevaadom.co.il/" target="_blank">צבע אדום</a>. last checked: {nowstr}</b>
                 '''
    ##
    for ytype in ['linear', 'log']:
        layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig = go.Figure(layout=layout)
        colors = ["#028a0f", "#000000", "#ad001d", "#ff2800", "#ff7900", "#fcd12a"][::-1]

        for column in range(n_lines):
            name = df.columns[column+1]
            fig.add_trace(go.Scatter(x=dateu, y=df[name],
                          name=name,
                          mode='markers',
                          line=dict(color=colors[column]),
                          marker=dict(
                              size=5,
                              color=colors[column],  # set color equal to a variable
                          )))
        for column in range(n_lines):
            name = df.columns[column+1]
            y = df[name].values.copy()
            for ii in range(4, len(y)-3):
                y[ii] = np.mean(y[ii-3:ii+4])
            y[0:4] = np.nan
            y[-3:] = np.nan
            fig.add_trace(go.Scatter(x=dateu, y=y,
                          name=name,
                          mode='lines',
                          line=dict(color=colors[column]),
                          marker=dict(
                              size=5,
                              color=colors[column],  # set color equal to a variable
                          )))
        fig.update_layout(
            title="Rockets alarms by date and distance from Gaza, and Rockets alarms from Lebanon (all distances)",
            xaxis_title="Time",
            yaxis_title="N alarm events")
        fig.update_xaxes(showline=False, linewidth=1, linecolor='lightgray', gridcolor='black')
        fig.update_xaxes(tickangle=45,
                         tickmode='array',
                         tickvals=datex,
                         ticktext=ticks)
        fig.update_yaxes(showgrid=True, gridwidth=1, zerolinecolor='lightgray', gridcolor='lightgray', side='left',
                         type=ytype)  # type='log'  range=(0, 3)
        # fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
        for leg in range(n_lines, n_lines*2):
            fig['data'][leg]['showlegend'] = False
        # fig['data'][0]['showlegend'] = False
        # fig.update_layout(showlegend=False)
        html = fig.to_html()
        html = html + tail_html
        # html += 'by .  <a href=https://datadashboard.health.gov.il/api/corona/hospitalizationStatus>source</a>'
        opfn = f'docs/alarms_by_date_and_distance_{ytype}.html'
        opfn = opfn.replace('_linear', '')
        with open(opfn, 'w') as f:
            f.write(html)
        if ytype == 'linear':
            opfn = opfn.replace('docs', 'data').replace('.html', '.csv')
            df.to_csv(opfn, index=False)
except Exception as e:
    print('war23_distance.py failed')
    a = os.system('echo "war23_distance.py failed" >> code/errors.log')
    b = os.system(f'echo "{e}" >> code/errors.log')


