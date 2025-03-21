import pandas as pd
import os
import numpy as np
import sys
import json


db = pd.read_csv('data/oct7database.csv')
idf = np.sum(db['הנצחה'].str.contains('idf'))
police = np.sum(db['הנצחה'].str.contains('police'))
shabak = np.sum(db['הנצחה'].str.contains('shabak'))

# sys.path.append('code')

# # df = pd.read_json('/home/innereye/Downloads/Telegram Desktop/ChatExport_2024-10-18/result.json')
# file = '/home/innereye/Downloads/Telegram Desktop/ChatExport_2024-10-18/result.json'
# f = open(file)
# data = json.load(f)
# f.close()
# # df = pd.DataFrame(columns=['date', 'text'])
# # for ii in range(len(data['messages'])):
# #     date = data['messages'][ii]['date'].replace('T', ' ')
# #     text = data['messages'][ii]['text']
# #     df.at[ii, 'date'] = date
# #     df.at[ii, 'text'] = text
# #     print(ii)
# # df = df[df['date'] > '2023-10-07']
# # df.to_excel('~/Documents/tsahal.xlsx')


# messages = []
# for message in data['messages']:
#     if 'date' in message and 'text' in message:
#         # Handle both cases where 'text' is a string or a list (in case of formatting markers)
#         if isinstance(message['text'], list):
#             text = ''.join([str(item) if isinstance(item, str) else '' for item in message['text']])
#         else:
#             text = message['text']
#         text = text.replace('דובר צה״ל:', '').replace('דובר צה"ל:', '').strip()
#         messages.append({
#             'date': message['date'].replace('T', ' '),
#             'text': text
#         })

# # Create a DataFrame and export it to Excel
# df1 = pd.DataFrame(messages)
# df1 = df1[df1['date'] > '2023-10-07']
# df1.to_excel('~/Documents/tsahal_cg.xlsx', index=False)
