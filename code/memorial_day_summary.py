import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go

os.chdir('/home/yuval/alarms')

df = pd.read_csv('data/oct7database.csv')
# add = pd.read_csv('data/oct7database_additional.csv')

# Combine, drop duplicates by pid
# df = pd.concat([table, add], ignore_index=True)
# df = df.drop_duplicates(subset='pid', keep='first')

# Filter: killed (main table) or died (additional table)
df = df[df['Status'].str.contains('killed|died', case=False, na=False)].copy()

# Parse death date
df['Death date'] = pd.to_datetime(df['Death date'], errors='coerce')

# Memorial day boundaries
memorial_days = [
    pd.Timestamp('2022-05-04'),
    pd.Timestamp('2023-04-25'),
    pd.Timestamp('2024-05-13'),
    pd.Timestamp('2025-04-30'),
    pd.Timestamp('2026-04-21'),
]

def assign_year(dt):
    if pd.isna(dt):
        return None
    for i, md in enumerate(memorial_days):
        if dt <= md:
            return md.year
    return None  # after last memorial day

df['year'] = df['Death date'].apply(assign_year)
df = df[df['year'].notna()]

# Memorial URL column name
mem_col = 'הנצחה'

def classify(row):
    url = str(row[mem_col]) if pd.notna(row[mem_col]) else ''
    role = str(row['Role']) if pd.notna(row['Role']) else ''
    has_idf = 'idf' in url.lower()
    has_laad = 'laad' in url.lower()
    has_memorial = len(str(row[mem_col])) > 3  # discount 'nan'

    if role == 'כיתת כוננות':
        return 'C'
    if has_idf and role == 'חייל':
        return 'A'
    if has_idf and role == 'אזרח':
        return 'B'
    if has_laad:
        return 'D'
    if not has_memorial and role == 'אזרח':
        return 'E'
    return 'Other'

df['group'] = df.apply(classify, axis=1)

# Count per year and group
years = sorted(df['year'].unique().astype(int))
groups = ['A', 'B', 'C', 'D', 'E']
group_labels = {
    'A': 'חללי צה"ל שנפלו בתפקיד',
    'B': 'חללי צה"ל שנרצחו כאזרחים',
    'C': 'אזרחים שנפלו בתפקיד (כיתת כוננות)',
    'D': 'אזרחים שנרצחו',
    'E': 'שוהים בלתי חוקיים שנרצחו',
}
colors = {
    'A': '#2d6a2d',
    'B': '#90c990',
    'C': '#1a3a8f',
    'D': '#00bcd4',
    'E': '#8e24aa',
}

counts = df.groupby(['year', 'group']).size().unstack(fill_value=0)

fig = go.Figure()
for g in ['D', 'C', 'A', 'B']:
    if g not in counts.columns:
        continue
    fig.add_trace(go.Bar(
        name=group_labels[g],
        x=[str(int(y)) for y in counts.index],
        y=counts[g],
        marker_color=colors[g],
        text=counts[g],
        textposition='inside',
        insidetextanchor='middle',
        textangle=0,
        textfont=dict(size=13, color='black' if g in ['B','E'] else 'white'),
        constraintext='none',
    ))

fig.update_layout(
    barmode='stack',
    title='קורבנות חרבות ברזל לפי שנה וקטגוריה',
    xaxis_title='שנת זיכרון',
    yaxis_title='מספר החללים',
    legend_title='',
    xaxis=dict(type='category'),
)

fig.show()

for y in range(2024, 2027):
    print(f"\n{y}")
    ur = df[(df['year'] == y) & (df['group'] == 'E')]
    for _, row in ur.iterrows():
        print(f"{row['pid']} {row['שם פרטי']} {row['שם משפחה']}")
print('civillian soldiers')
year = 2025
ur = df[(df['year'] == year) & (df['group'] == 'B')]
for _, row in ur.iterrows():
    print(f"{row['pid']} {row['שם פרטי']} {row['שם משפחה']}")
print('export murdered')
year = 2026
group = 'D'
ur = df[(df['year'] == year) & (df['group'] == group)]
ur.to_excel(f'~/Documents/memorial_{year}_{group}.xlsx', index=False)

print('capau')