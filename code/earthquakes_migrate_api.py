import pandas as pd
import os
import requests
url = os.environ['Seismo']
response = requests.get(url+'?startDate=2000-01-04&endDate=2011-01-01')
data = response.json()
df0 = pd.DataFrame(data['earthquakes'])
response = requests.get(url+'?startDate=2011-01-01&endDate=2016-01-01')
data = response.json()
df1 = pd.DataFrame(data['earthquakes'])
response = requests.get(url+'?startDate=2016-01-01&endDate=2020-01-01')
data = response.json()
df2 = pd.DataFrame(data['earthquakes'])
response = requests.get(url+'?startDate=2020-01-01&endDate=2023-01-01')
data = response.json()
df3 = pd.DataFrame(data['earthquakes'])
response = requests.get(url+'?startDate=2023-01-01&endDate=2025-01-01')
data = response.json()
df4 = pd.DataFrame(data['earthquakes'])
response = requests.get(url+'?startDate=2025-01-01&endDate=2026-05-20')
data = response.json()
df5 = pd.DataFrame(data['earthquakes'])
# print(data['total'])
df = pd.concat([df0,df1,df2,df3,df4,df5][::-1])
old = pd.read_csv('data/earthquakes.csv')
old.to_csv('data/earthquakes2026.csv', index=False)
df.to_csv('data/earthquakes.csv', index=False)


