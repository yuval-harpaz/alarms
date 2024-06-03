import pandas as pd
from selenium import webdriver
import os
# from pyvirtualdisplay import Display
import time
import numpy as np

local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True
##
data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
kidn = pd.read_csv('data/kidnapped.csv')
for ii in range(len(kidn)):
    name = kidn['name'][ii].split()
    row = np.where(
        data['שם פרטי'].str.contains(kidn['first'][ii]) &
        data['שם משפחה'].str.contains(kidn['last'][ii]))[0]
    if len(row) == 1:
        kidn.at[ii, 'pid'] = data['pid'][row[0]]
# data = data[~data['הנצחה'].isnull()]
# data.reset_index(drop=True, inplace=True)
# browser = webdriver.Firefox()
# colall = list(data.columns[1:9])
# colheb = list(data.columns[5:9])
# for ii in range(len(data)):
#     url = data['הנצחה'][ii]
#     browser.get(url)
#     time.sleep(0.1)
#     html = browser.page_source
#     if '.idf.' in url:
#         columns = colall
#     else:
#         columns = colheb
#     issue = ''
#     for col in columns:
#         nm = data[col][ii]
#         if str(nm) != 'nan':
#             if nm not in html:
#                 issue = issue + ' ' + nm
#     if issue == '':
#         issue = np.nan
#     else:
#         issue = issue.strip()
#     data.at[ii, 'issues'] = issue
#
# # data = data[~data['issues'].isnull()]
# data.to_csv('/home/innereye/Documents/issues_url.csv', index = False)
# ##
# for ii in range(954, len(data)):
#     url = data['הנצחה'][ii]
#     if '.btl.' not in url:
#         browser.get(url)
#         time.sleep(0.1)
#         html = browser.page_source
#         if '.idf.' in url:
#             columns = colall
#         else:
#             columns = colheb
#         issue = ''
#         for col in columns:
#             nm = data[col][ii]
#             if str(nm) != 'nan':
#                 if nm not in html:
#                     issue = issue + ' ' + nm
#         if issue == '':
#             issue = np.nan
#         else:
#             issue = issue.strip()
#         data.at[ii, 'issues'] = issue
#     else:
#         data.at[ii, 'issues'] = np.nan
#
# ##
# data = pd.read_csv('/home/innereye/Documents/issues_url.csv')
# colall = list(data.columns[1:9])
# colheb = list(data.columns[5:9])
# browser = webdriver.Firefox()
# for ii in range(760, len(data)):
#     url = data['הנצחה'][ii]
#     if '.btl.' in url:
#         time.sleep(1.05)
#         browser.get(url)
#         time.sleep(0.1)
#         html = browser.page_source
#         if '.idf.' in url:
#             columns = colall
#         else:
#             columns = colheb
#         issue = ''
#         for col in columns:
#             nm = data[col][ii]
#             if str(nm) != 'nan':
#                 if nm not in html:
#                     issue = issue + ' ' + nm
#         if issue == '':
#             issue = np.nan
#         else:
#             issue = issue.strip()
#         data.at[ii, 'issues'] = issue
#     # else:
#         # data.at[ii, 'issues'] = np.nan
# #
# data.to_csv('/home/innereye/Documents/issues_url.csv', index = False)
# data = data[~data['issues'].isnull()]
# data.to_csv('/home/innereye/Documents/issues_url_gist.csv', index = False)