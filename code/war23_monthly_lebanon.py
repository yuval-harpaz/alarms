import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

df = pd.read_csv('data/alarms_by_date_and_distance.csv')
month = np.array([x[:7] for x in df['date'].values])
monthu = np.unique(month)
monthly = pd.DataFrame(columns=['date', 'rockets', 'drones'])
for imonth in range(len(monthu)):
    row = [monthu[imonth],
           int(np.sum(df['Lebanon'].values[month == monthu[imonth]])),
           int(np.sum(df['Lebanon_drone'].values[month == monthu[imonth]]))]
    monthly.loc[len(monthly)] = row
co = np.array([[209, 43, 167], [255, 222, 89]])
co = co/255
x = np.arange(len(monthu))
plt.figure()
plt.bar(x-0.2, monthly['drones'], 0.3, color=co[1, :], label='UAVs')
plt.bar(x+0.2, monthly['rockets'], 0.3, color=co[0, :], label='Rockets')

plt.legend()
plt.xticks(x, monthu, rotation=90)
plt.gca().yaxis.grid()
plt.gca().set_axisbelow(True)
plt.title('Alarm events triggered by Lebanon, by month and alarm type')
plt.ylabel('Alarm events per month')