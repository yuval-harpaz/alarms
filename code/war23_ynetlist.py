'''
read the table from ynet https://www.ynet.co.il/news/category/51693
NOTE - info is from the media, not formal and not validated, use with care
'''
print('ynetlist is buggy, got to restore data/ynetlist.csv from backup')
if False:
    import pandas as pd
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    import time
    import requests
    import os
    import numpy as np
    import re
    import json
    from glob import glob


    try:
        local = '/home/innereye/alarms/'
        if os.path.isdir(local):
            os.chdir(local)
            local = True
        prev = pd.read_csv('data/ynetlist.csv')
        # dfprev = pd.read_csv('data/ynetlist.csv')
        # url = 'https://atlas.jifo.co/api/connectors/9c8936a5-bd30-4d68-9715-7280389e094c'
        # url = 'https://www.ynet.co.il/news/category/51693'
        url = "https://e.infogram.com/e7de0f19-b7b4-4a33-b23e-5037fde484d1?src=embed"
        r = requests.get(url)
        html = r.text
        if 'xlsx' in html:
            # find xlsx url in html
            xlsx_url = html[:html.index('xlsx') + 4][::-1]
            xlsx_url = xlsx_url[:xlsx_url.index('sptth')+5][::-1]
            decoded_url = json.loads(f'"{xlsx_url}"')
            # xlsx_url = re.search(r'https://ynet-pic1.yit.co.il/picserver5/wcm_upload_files/.*?\.xlsx', html)
            # url = 'https://ynet-pic1.yit.co.il/picserver5/wcm_upload_files/2023/11/08/BJsj8pO76/ynetlist711.xlsx'
            download_dir = os.path.abspath("downloads")
            os.makedirs(download_dir, exist_ok=True)
            options = Options()
            options.add_argument("--headless=new")  # Remove this if you want to see the browser
            options.add_experimental_option("prefs", {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(decoded_url)
            time.sleep(5)
            xlsx_path = glob(os.path.join(download_dir, '*.xlsx'))[0]
            df = pd.read_excel(xlsx_path)
            prev_str = [';'.join(x).replace('nan','').replace('.0;',';') for x in prev.values[:, :-1].astype(str)]
            df_str = [';'.join(x).replace('nan','').replace('.0;',';') for x in df.values.astype(str)]
        if prev_str == df_str:
            df = prev
        else:
            df['pid'] = np.nan
            # some changes in new ynet list
            df_str = np.array(df_str)
            prev_str = np.array(prev_str)
            for ii in range(len(df)):
                prev_row = np.where(prev_str == df_str[ii])[0]
                if len(prev_row) == 1:
                    df.at[ii, 'pid'] = prev['pid'][prev_row[0]]
            print('updated ynetlist')
            df.to_csv('data/ynetlist.csv', index=False)
        db = pd.read_csv('data/oct7database.csv')
        added = False
        for iy in np.where(df['pid'].isnull())[0]:
            indb = db['שם פרטי'].str.replace('׳',"'").str.contains(str(df['שם פרטי'][iy])) & \
                db['שם משפחה'].replace('׳',"'").str.contains(str(df['שם משפחה'][iy])) & \
                db['Residence'].str.contains(df['מקום מגורים'][iy])
            indb = np.where(indb)[0]
            if len(indb == 1):
                pid = db['pid'][indb[0]]
                if pid not in df['pid'].values:
                    df.at[iy, 'pid'] = pid
                    print(f'added pid {pid} to ynet')
                    added = True
        if added:
            print('found PIDs for ynetlist')
            df.to_csv('data/ynetlist.csv', index=False)
        print('done ynet')
        # browser.close()
    except Exception as e:
        print('war23_ynetlist.py failed')
        a = os.system('echo "war23_ynetlist.py failed" >> code/errors.log')
        b = os.system(f'echo "{e}" >> code/errors.log')
