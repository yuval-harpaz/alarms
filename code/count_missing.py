import pandas as pd
import numpy as np
import os
import json

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

dfm = pd.read_excel(os.path.expanduser('~/Documents/n_missing.xlsx'))
coo = pd.read_csv('data/coord.csv')

dfm['lat'] = np.nan
dfm['lon'] = np.nan
missing = []
for iloc, loc in enumerate(dfm['cities'].values):
    key = str(loc).split(',')[0].strip()
    row = np.where(coo['loc'] == key)[0]
    if len(row) == 0:
        missing.append(key)
        continue
    dfm.at[iloc, 'lat'] = coo['lat'][row[0]]
    dfm.at[iloc, 'lon'] = coo['long'][row[0]]

if missing:
    print('Missing coordinates for:', missing)

# Build JSON for the map
records = []
for _, r in dfm.dropna(subset=['lat', 'lon']).iterrows():
    records.append({
        'cities': str(r['cities']),
        'n': int(r['n']),
        'lat': float(r['lat']),
        'lon': float(r['lon'])
    })

data_json = json.dumps(records, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>אזעקות חסרות לפי מיקום</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" />
  <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css" />
  <style>
    #map {{ height: 100vh; width: 100%; }}
    #floating-title {{
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255,255,255,0.85);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 1.4em;
      font-weight: 500;
      box-shadow: 0 0 4px rgba(0,0,0,0.2);
      z-index: 1000;
      direction: rtl;
      text-align: center;
    }}
    .legend {{
      background: white;
      padding: 8px 12px;
      font-size: 1.5em;
      line-height: 1.6;
      border-radius: 6px;
      box-shadow: 0 0 5px rgba(0,0,0,0.3);
    }}
    .leaflet-control-attribution {{
      background: transparent !important;
      font-size: 14px;
      color: black;
      text-shadow: 0 0 3px white;
    }}
  </style>
</head>
<body>
  <div id="floating-title">אזעקות חסרות לפי מיקום</div>
  <div id="map"></div>
  <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
  <script>
    const data = {data_json};

    function isMobile() {{
      return /Mobi|Android/i.test(navigator.userAgent);
    }}
    const basic_size = isMobile() ? 6 : 3;

    const map = L.map('map').setView([31.5, 34.75], 8);
    L.tileLayer('https://cdnil.govmap.gov.il/xyz/heb/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '© המרכז למיפוי ישראל www.govmap.gov.il'
    }}).addTo(map);

    const total = data.reduce((s, d) => s + d.n, 0);

    data.forEach(d => {{
      const color = d.n === 1 ? 'gold' : d.n === 2 ? 'orange' : 'red';
      const popup = `<div dir="rtl" style="text-align:right; font-size:1.3em;">
        ${{d.cities}}<br>מספר אזעקות: ${{d.n}}</div>`;
      L.circleMarker([d.lat, d.lon], {{
        radius: basic_size + 4,
        fillColor: color,
        color: color,
        weight: 1,
        opacity: 1,
        fillOpacity: 0.7
      }}).addTo(map).bindPopup(popup);
    }});

    const legend = L.control({{ position: 'topleft' }});
    legend.onAdd = function() {{
      const div = L.DomUtil.create('div', 'legend');
      div.innerHTML = `<div dir="rtl" style="text-align:right;">
        <span style="color:gold;">● 1 אזעקה</span><br>
        <span style="color:orange;">● 2 אזעקות</span><br>
        <span style="color:red;">● 3 אזעקות</span><br>
        סה"כ: ${{total}}
      </div>`;
      return div;
    }};
    legend.addTo(map);
  </script>
</body>
</html>"""

out_path = os.path.expanduser('~/Documents/n_missing_map.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Saved to {out_path}')
