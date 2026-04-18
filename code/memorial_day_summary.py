import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

os.chdir('/home/yuval/alarms')

df = pd.read_csv('data/oct7database.csv')
# add = pd.read_csv('data/oct7database_additional.csv')

# Combine, drop duplicates by pid
# df = pd.concat([table, add], ignore_index=True)
# df = df.drop_duplicates(subset='pid', keep='first')
forces = True  # should be true to count police and shabak
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

def classify(row, forces=forces):
    url = str(row[mem_col]) if pd.notna(row[mem_col]) else ''
    role = str(row['Role']) if pd.notna(row['Role']) else ''
    has_idf = 'idf' in url.lower()
    has_laad = 'laad' in url.lower()
    has_memorial = len(str(row[mem_col])) > 3  # discount 'nan'
    is_ilia = row['pid'] == 2527
    if forces:
        category = 'Other'
        if role == 'כיתת כוננות':
            category = 'C'
        elif role in ['חייל', 'שב"כ', 'שוטר']:
            category = 'A'
        elif role == 'צוות רפואי':
            category = 'D'
        elif role == 'אזרח':
            if has_laad or is_ilia or not has_memorial:
                category = 'D'
            else:
                category = 'B'
        return category
    else:
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
if forces:
    for g in ['A', 'B']:
        group_labels[g] = group_labels[g].replace('חללי צה"ל', 'כוחות הבטחון')
colors = {
    'A': '#2d6a2d',
    'B': '#90c990',
    'C': '#1a3a8f',
    'D': '#00bcd4',
    'E': '#8e24aa',
}

counts = df.groupby(['year', 'group']).size().unstack(fill_value=0)

# Add pre-table victims for 2024
counts.loc[2024, 'A'] = counts.loc[2024, 'A'] + 6
counts.loc[2024, 'D'] = counts.loc[2024, 'D'] + 11 + 8  # 11 civil before 7.10, 5 Gazans and 3 africans not recognized

counts.index = counts.index.astype(int)
counts = counts.sort_index()

x_labels = [f"{y-1}–{y}" for y in counts.index]

fig = go.Figure()
for g in ['D', 'C', 'A', 'B']:
    if g not in counts.columns:
        continue
    fig.add_trace(go.Bar(
        name=group_labels[g],
        x=x_labels,
        y=counts[g].values,
        marker_color=colors[g],
        text=counts[g].values.astype(int),
        textposition='inside',
        insidetextanchor='middle',
        textangle=0,
        textfont=dict(size=13, color='black' if g in ['B', 'E'] else 'white'),
        constraintext='none',
    ))

# Total annotations on top of each bar
visible_groups = [g for g in ['D', 'C', 'A', 'B'] if g in counts.columns]
totals = counts[visible_groups].sum(axis=1).values
annotations = [
    dict(
        x=x_labels[i],
        y=totals[i],
        text=f"<b>{int(totals[i])}</b>",
        xanchor='center',
        yanchor='bottom',
        showarrow=False,
        font=dict(size=14),
    )
    for i in range(len(x_labels))
]

fig.update_layout(
    barmode='stack',
    title=dict(
        text='קורבנות חרבות ברזל לפי שנה וקטגוריה',
        x=0.85,
        xanchor='right',
    ),
    xaxis_title='שנת זיכרון',
    yaxis_title='מספר החללים',
    legend_title='',
    xaxis=dict(type='category'),
    legend=dict(
        x=0.99,
        y=0.99,
        xanchor='right',
        yanchor='top',
        bgcolor='rgba(255,255,255,0.7)',
        bordercolor='gray',
        borderwidth=1,
    ),
    height=880,
    width=500,
    margin=dict(b=120),
    annotations=annotations + [
        dict(
            text='oct7database.com : נתונים',
            xref='paper', yref='paper',
            x=1.0, y=1.07,
            xanchor='right', yanchor='top',
            showarrow=False,
            font=dict(size=12, color='gray'),
        )
    ],
)

fig.show()

# ── Page 2: pie charts by front, per year, security forces vs civilians ──────
security_roles = ['חייל', 'שב"כ', 'שוטר', 'כבאי', 'כיתת כוננות', 'צוות רפואי']
civilian_roles = ['אזרח']

pie_years = [2024, 2025, 2026]
pie_year_labels = {y: f"{y-1}–{y}" for y in pie_years}

front_colors = {
    'Gaza':      '#c0392b',
    'North':     '#2980b9',
    'Iran':      '#8e44ad',
    'West Bank': '#e67e22',
    'Home':      '#27ae60',
    'Other':     '#7f8c8d',
    'Jordan':    '#f39c12',
    'Accident':  '#95a5a6',
    'Iraq':      '#d35400',
    'Yemen':     '#16a085',
}

fig2 = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        f'{cat} – {pie_year_labels[y]}'
        for cat in ['כוחות ביטחון', 'אזרחים']
        for y in pie_years
    ],
    specs=[[{'type': 'domain'}] * 3] * 2,
)

for col_i, y in enumerate(pie_years, start=1):
    year_df = df[df['year'] == y]
    sec_df  = year_df[year_df['Role'].isin(security_roles)]
    civ_df  = year_df[year_df['Role'].isin(civilian_roles)]

    for row_i, sub_df in enumerate([sec_df, civ_df], start=1):
        front_counts = sub_df['front'].value_counts(dropna=False)
        front_counts.index = front_counts.index.fillna('Other')
        labels = list(front_counts.index)
        values = list(front_counts.values)
        pie_colors = [front_colors.get(l, '#bdc3c7') for l in labels]
        fig2.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=pie_colors),
                textinfo='label+value',
                showlegend=False,
            ),
            row=row_i, col=col_i,
        )

fig2.update_layout(
    title=dict(text='חללים לפי חזית – כוחות ביטחון ואזרחים', x=0.5),
    height=600,
    width=1050,
)
fig2.show()

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