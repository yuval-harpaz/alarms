import pandas as pd
import numpy as np
import os
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
    dfwar = dfwar[dfwar['origin']  == 'Gaza']
    dfwar = dfwar.reset_index(drop=True)
    date = np.array([d[:10] for d in dfwar['time']])
    dateu = np.unique(date)
    coo = pd.read_csv('data/coord.csv')
    coo = pd.read_csv('data/coord_km_gaza.csv')
    edges = [0, 7, 15, 30, 50, 300]
    hist = np.zeros((len(edges)-1, len(dateu)))
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
        hist[:, day] = np.histogram(dist, edges)[0]
    ##
    df = pd.DataFrame(dateu, columns=['date'])
    for irange in range(len(edges) - 1):
        df[(str(edges[irange])+'-'+str(edges[irange+1])).replace('-300', '+')] = hist[irange, :]

    ##
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig = go.Figure(layout=layout)
    colors = ["#000000", "#ad001d", "#ff2800", "#ff7900", "#fcd12a"][::-1]
    for column in range(5):
        name = df.columns[column+1]
        fig.add_trace(go.Scatter(x=dateu, y=df[name],
                      name=name,
                      mode='markers',
                      line=dict(color=colors[column]),
                      marker=dict(
                          size=5,
                          color=colors[column],  # set color equal to a variable
                      )))
    for column in range(5):
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
        title="Rockets alarms by time and distance from Gaza",
        xaxis_title="Time",
        yaxis_title="N alarm events")
    fig.update_xaxes(showline=False, linewidth=1, linecolor='lightgray', gridcolor='black')
    fig.update_yaxes(showgrid=True, gridwidth=1, zerolinecolor='lightgray', gridcolor='lightgray', side='left',
                     type='log')  # type='log'  range=(0, 3)
    # fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
    for leg in range(5, 10):
        fig['data'][leg]['showlegend'] = False
    # fig['data'][0]['showlegend'] = False
    # fig.update_layout(showlegend=False)
    html = fig.to_html()
    with open('docs/alarms_by_date_and_distance.html', 'w') as f:
        f.write(html)
except:
    print('distance plotly chart failed')

##  Old code
# long[irow] = coo['long'][coo['loc'] == dfwar['cities'].values[row]].values[0]
# for g in Gaza:
#     d.append(geodesic([np.median(lat), np.median(long)], g).km)
# dist[iid] = np.min(d)
# Gaza = np.array([34.490547, 31.596096, 34.5249, 31.5715, 34.559166, 31.546944, 34.558609, 31.533054,
#                  34.539993, 31.514721, 34.513329, 31.498608, 34.478607, 31.471107, 34.4337, 31.4329,
#                  34.388885, 31.394722, 34.364166, 31.360832, 34.373604, 31.314442, 34.334160, 31.259720,
#                  34.267578, 31.216541])
# Gaza = Gaza.reshape(int(len(Gaza)/2), 2)[:, [1, 0]]
#
# c = 0
# for col in range(5):
#     c += 0.2
#     fig = px.scatter(df, x="date", y=df.columns[col+1], color=c)
    # fig = px.scatter(df, x="date", y=df.columns[1:])
# fig.show()

# plt.figure()
# plt.plot(hist.T)
#
# ##
# plt.figure()
# for day in range(len(dateu)):
#     # plt.subplot(4,7,day+1)
#     if dateu[day] > '2023-10-27':
#         color = 'b'
#     elif dateu[day] == '2023-10-07':
#         color = 'k'
#     else:
#         color = 'r'
#     plt.plot(edges[1:-1], hist[:-1, day], color)
# plt.grid()
# dates = [[0], np.arange(1, 21), np.arange(21, len(dateu)+1)]
# group = [[0], [1], [2,3], range(4, len(edges)-1)]
# means = np.zeros((len(group), len(dates)))
# for ig, gg in enumerate(group):
#     for id, dd in enumerate(dates):
#         means[ig, id] = hist[gg, id].sum()/len(dd)
# ##
# shift = [-0.3, -0.1, 0.1, 0.3]
# plt.figure()
# for ig in range(len(group)):
#     plt.bar(np.arange(len(dates)) + shift[ig], means[ig, :], 0.2)
# plt.xticks(range(3), ['day 0','before invasion', 'after invasion'])
# plt.legend(['<5', '5-10', '10-20', '20+'])
#
#
# ##
# plt.figure()
# plt.plot(dateu, near, label='less than 20km')
# plt.plot(dateu, far, label='more than 20km')
# plt.legend()
# plt.grid()
# plt.xticks(rotation=90)
#
# fig = px.bar(x=dateu, y=n, log_y=True)
# # fig = px.bar(prev, y=n, x='date',log_y=True)
# html = fig.to_html()
# file = open('docs/alarms_last_7_days.html', 'w')
# a = file.write(html)
# file.close()
# #
# #
# # df = pd.read_csv('data/deaths.csv')
# # # coo = pd.read_csv('data/coord.csv')
# # locs = [x for x in df['from'] if type(x) == str]
# # locu = np.unique(locs)
# # for md in list(min_deaths.keys()):
# #     if md not in locu:
# #         locu = np.array(list(locu) + [md])
# # update_coord(latest=locu, coord_file='data/coord_deaths.csv')
# # coo = pd.read_csv('data/coord_deaths.csv')
#
# ##
# if 0 > 1:
#     center = [coo['lat'].mean(), coo['long'].mean()]
#     coo = pd.read_csv('data/coord_deaths.csv')
#     center = [coo['lat'].mean(), coo['long'].mean()]
#     map = folium.Map(location=center, zoom_start=7.5)  # , tiles='openstreetmap')
#     folium.TileLayer('cartodbpositron').add_to(map)
#     locu = Gaza
#     for iloc in range(len(locu)):
#         lat = locu[iloc, 0]
#         long = locu[iloc, 1]
#         # long = float(coo['long'][coo['loc'] == locu[iloc]])
#         tip = str(iloc)
#         folium.Circle(location=[lat, long],
#                       tooltip=tip,
#                       radius=1,
#                       fill=True,
#                       fill_color='#ff0000',
#                       color='#ff0000',
#                       opacity=0,
#                       fill_opacity=0.5
#                       ).add_to(map)
#     map.save("/home/innereye/Documents/gaza.html")
#     print('done')

# now = np.datetime64('now', 'ns')
# nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
# nowstr = str(nowisr)[:16].replace('T', ' ')
# current_date = datetime.now()
# date_list = []
# for idate in range(len(dateu)):
#     date_list.append(current_date.strftime('%Y-%m-%d'))
#     current_date -= timedelta(days=1)