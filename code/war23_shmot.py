import pandas as pd
# import os
# # import Levenshtein
# import numpy as np
# import re
import requests

js = requests.get('https://oct7names.co.il/assets/index-af79e9f3.js').text
txt = js[js.index('Kf=')+3:js.index('Yf=')-1]
txt = txt.replace('מפקד בי"ס לוט"ר', 'מפקד בית ספר ללוחמה בטרור')
segs = txt.split('{')
iseg = 1
seg = segs[iseg].split(',')[:-1]
col = [x[:x.index(':')] for x in seg]
df = pd.DataFrame(columns=col)
for iseg in range(1,len(segs)):
    seg = segs[iseg]
    # seg = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', seg)
    for icol in range(len(col)):
        cn = col[icol]
        if cn in seg:
            fro = seg.index(cn)
            tail = seg[fro:]
            tail = tail[tail.index(':')+1:]
            if ':' in tail:
                next = min([tail.index(x) for x in col[icol+1:] if x in tail])
                val = tail[1:next-2]
            else:
                val = tail[1:-3]
            df.at[iseg - 1, cn] = val

df.to_csv('data/shmot.csv', index=False)
    #
    #     else:
    #         print(f'{iseg} {cn} not found')
    #     next = seg[fro:]
    #         co = field[:field.index(':')]
    #         field = field[field.index(':')+1:]
    #         sep = field[0]
    #         field = field[field.index(sep)+1:]
    #         field = field[:field.index(sep)]
    #         df.at[iseg-1, co] = field
    #     except:
    #         print(f'{iseg}: {field}')
    # # df.loc[len(df)] = row


for field in seg[:-1]:
    co = field[:field.index(':')]
    field = field[field.index(':')+1:]
    sep = field[0]
    field = field[field.index(sep)+1:]
    field = field[:field.index(sep)]
    df.at[iseg-1, co] = field