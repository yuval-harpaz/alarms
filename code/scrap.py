import pandas as pd

shamap = pd.to_datetime(['2023-10-08', '2023-10-11', '2023-12-08'])
trans = pd.to_datetime('2023-10-09')
dif = shamap-trans
zero = pd.Timedelta('0 days')
if min(dif) >= zero:  # no negative (no shamap before transfer)
    keep = min(dif)
else:  # some shamap are before transfer
    if all(dif < zero):  # only shamaps before, take last one
        keep = max(dif)
    else:  # some pos some neg, take smallest positive
        keep = min(dif[dif > zero])





