import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from xlsxwriter.utility import xl_rowcol_to_cell

import projections
from projections import CATEGORIES, META

def unify_projections():
    df = projections.fetch_all()
    average = df.groupby('name')[CATEGORIES].mean().reset_index()
    meta = df[df['source'] == 'numberFire'][['name', 'team', 'position']]
    secondary = df[df['source'] == 'Daily Faceoff'][['name', 'position']]
    meta = pd.merge(meta, secondary, how='left', on='name', suffixes=('', '_alt'))
    players = pd.merge(meta, average, how='left', on='name')
    players.loc[players['position'] == players['position_alt'], 'position_alt'] = None
    return players

df = unify_projections()

# clean

for column in ['wins', 'goals_against_average',
        'saves', 'save_percentage','shutouts' ]:
    df.loc[df['position'] != 'G', column] = 0
for column in ['goals', 'assists', 'plus_minus',
        'powerplay_points', 'shots_on_goal', 'hits', 'blocks']:
    df.loc[df['position'] == 'G', column] = 0

df['hits'] = SimpleImputer().fit_transform(df[['hits']]).ravel()
df['blocks'] = SimpleImputer().fit_transform(df[['blocks']]).ravel()
df['shutouts'] = SimpleImputer().fit_transform(df[['shutouts']]).ravel()
# GAA is a bad thing, need to reverse
df['goals_against_average'] = -df['goals_against_average']

df[CATEGORIES] = (
    df[CATEGORIES]
    .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
)
df.loc[df['position'] != 'G', 'goals_against_average'] = 0
df.loc[df['position'] == 'G', 'plus_minus'] = 0

df['STICKY_SCORE'] = df[CATEGORIES].sum(axis=1)

# pool particulars
pool_size = 12
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}

players = sum(starters.values())
skaters = sum([value for key, value in starters.items() if key != 'G'])
goalies = players - skaters
df['STICKY_SCORE'] = df['STICKY_SCORE'] / players
df['STICKY_SCORE'] = np.where(df['position'] == 'G', df['STICKY_SCORE'] / goalies, df['STICKY_SCORE'] / skaters)

for position, slots in starters.items():
    replacement = (
        df[df['position'] == position]
        .sort_values('STICKY_SCORE', ascending=False)
        .head(slots * pool_size)
        ['STICKY_SCORE']
        .mean()
    )
    df.loc[df['position'] == position, 'STICKY_SCORE'] = df['STICKY_SCORE'] - replacement

# MAXSCORE
df['STICKY_SCORE'] = df[['STICKY_SCORE']].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
df['STICKY_RANK'] = df['STICKY_SCORE'].rank(method='average', ascending=False)
df = df.sort_values('STICKY_RANK')

# ARBITRAGE
yahoo = projections.yahoo_draft_rankings()
df = pd.merge(df, yahoo, how='left', on='name')
df['arbitrage'] = df['yahoo'] - df['STICKY_RANK']
df['round'] = (df['yahoo'] / pool_size) + 1

# CAPFRIENDLY

cap = projections.capfriendly()
df = pd.merge(df, cap, how='left', on='name')

# FORMATING

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('draft/sticky.xlsx', engine='xlsxwriter', options={'nan_inf_to_errors': True})

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(excel_writer=writer, sheet_name='draft', index=False)

workbook  = writer.book
worksheet = writer.sheets['draft']

# find area to format
first = df.columns.get_loc(CATEGORIES[0])
first_column = xl_rowcol_to_cell(1, first)[0]
last = df.columns.get_loc(CATEGORIES[-1])
last_column = xl_rowcol_to_cell(1, last)[0]
first_row = 2
last_row = df.shape[0] + 1
area = f'{first_column}{first_row}:{last_column}{last_row}'

# add formatting
percent_format = workbook.add_format({'num_format': '0.0%'})
worksheet.set_column(f'{area}', None, percent_format)
worksheet.conditional_format(f'{area}', {'type': '3_color_scale'})

# convert to table
df = df.fillna('')
last_column = xl_rowcol_to_cell(0, len(df.columns)-1)[0]
data = [[i for i in row] for row in df.itertuples(index=False)]
header = [{'header': c} for c in df.columns]
worksheet.add_table(
    f'A1:{last_column}{last_row}',
    {'data': data, 'columns': header,
    'style': 'Table Style Light 1'}
)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
