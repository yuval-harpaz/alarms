# sudo apt-get install exiftool
# pip install pyexiftool
import os
import exiftool
from glob import glob
import numpy as np
import pandas as pd

os.chdir('/home/innereye/Videos')
# f = open('road1.mp4', 'rb')
# tags = exiftool.process_file(f)
# ffmpeg -i road1.mp4 -f ffmetadata road1.txt
# mediainfo road1.mp4
# exiftool -ExtractEmbedded road1.mp4
##
with exiftool.ExifToolHelper() as et:
    metadata = et.get_metadata('road1.mp4')

metadata = metadata[0]

for key in metadata.keys():
    val = str(metadata[key])
    if '31.' in val or '34.' in val:
        print(key+'   '+val)

##
os.chdir('/media/innereye/KINGSTON/War/meytal/')
search = ['*.*', '*/*.*', '*/*/*.*']
suf = []
for sc in search:
    suf += [x.split('.')[-1] for x in glob(sc) if ord(x.split('.')[-1][-1]) < 1488]
suf = np.unique(suf)
print('sufix: ', end='')
print(suf)
files = []
for sfx in ['mov', 'mp4']:
    for sc in search:
        files += glob(sc+sfx)
coo = []
for file in files:
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file)
    metadata = metadata[0]
    found = ''
    for key in metadata.keys():
        val = str(metadata[key])
        if '31.' in val and '34.' in val:
            print(key + '   ' + val)
            found = val
            break
    coo.append(found)
## TODO save creation date

for file in files:
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file)
    metadata = metadata[0]
    # found = []
    print(file)
    for key in metadata.keys():
        val = str(metadata[key])
        # print(key + '   ' + val)
        if 'creat' in key.lower():
            print(key + '   ' + val)
            # found = val
            # break
    # coo.append(found)
df = pd.DataFrame(columns=['file','CreateDate'])
for file in files:
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file)
    metadata = metadata[0]
    df.loc[len(df)] = [file, metadata['QuickTime:CreateDate']]
df.to_csv('CreateDate.csv', index=False)
##
import exifread
from PIL import Image


files = []
for sfx in ['png', 'jpeg', 'jpg']:
    for sc in search:
        files += glob(sc+sfx)

for file in files:
    f = open(file, 'rb')
    tags = exifread.process_file(f)
    # im = Image.open(file)
    if len(tags.keys()) > 0:
        for key in tags.keys():
            if 'location' in key.lower():
                print(file+'::: '+key+' '+tags[key])


for file in files:
    im = Image.open(file)
    print(file)
    print(im.info)
    print(getattr(im, '_getexif', lambda: None)())


file = 'תיקיה חומרים קודמים/8. יונדאי אפורה 2 הרוגים/Screenshot_20231024-232251_Telegram.jpg'
f = open(file, 'rb')
tags = exifread.process_file(f)
im = Image.open(file)
print(im.info)
