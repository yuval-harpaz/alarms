# sudo apt-get install exiftool
# pip install pyexiftool
import os
# import exiftool
# from glob import glob
import numpy as np
import pandas as pd
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
# os.chdir('/home/innereye/Videos')
# # f = open('road1.mp4', 'rb')
# # tags = exiftool.process_file(f)
# # ffmpeg -i road1.mp4 -f ffmetadata road1.txt
# # mediainfo road1.mp4
# # exiftool -ExtractEmbedded road1.mp4
##
df = pd.read_csv('data/victims_relationship.csv')
vals = df.values[:, 8:15].astype(str)
vals[vals == 'nan'] = ''
relatives = []
size = []
for ii in range(vals.shape[0]):
    rel = []
    for jj in range(vals.shape[1]):
        rel.extend(vals[ii, jj].split(';'))
    rel = [int(x) for x in rel if len(x) > 0]
    relatives.append(rel)
    size.append(len(rel))
##
group = np.zeros(len(size), int)
cur = 0
for ii in range(len(size)):
    pid = df['pid'][ii]
    imember = np.where([pid in x for x in relatives])[0]
    if len(imember) > 0:
        grp = np.unique(group[imember])
        grp1 = [x for x in grp if x > 0]
        if len(grp1) == 0:  # new family
            cur += 1
            group[imember] = cur
            group[ii] = cur
        else:
            if len(grp1) != 1:
                raise Exception('too many groups')
            else:
                group[imember] = grp1[0]
                group[ii] = grp1[0]
    df['group'] = group
df.to_csv('~/Documents/families.csv', index=False)








