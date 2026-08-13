import pandas as pd
import os
from war23_api import changed_pid, missing_pid, pid2record, send_records

if __name__ == '__main__':
    missing = missing_pid()
    if len(missing) > 0:
        print('n missing pid:', len(missing))
        for pid in missing:
            record = pid2record(pid)
            send_records(record)
        print('sent missing, check and run again for making changes')
        exit()
    changed = changed_pid()
    if len(changed) > 0:
        print('n changed pid:', len(changed))
        print('not updating, bugged')
        # for pid in changed.keys():
        #     send_records(changed[pid])


