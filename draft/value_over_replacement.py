import sqlite3
import pandas as pd
import numpy as np

pd.options.display.max_rows = 999
con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# aggregate

sql = '''
    select * from draft_espn
    union all
    select * from draft_fantasy_pros
    union all
    select * from draft_fantasy_pros
    union all
    select * from draft_nfl
    union all
    select * from draft_numberfire
'''

df = pd.read_sql(sql, con)
df = df.infer_objects()
df['points'] = pd.to_numeric(df['points'])
df_agg = df.groupby('name')['points'].agg({
    'count': 'count',
    'mean': 'mean',
    'std': 'std',
    'min': 'min',
    'max': 'max'
})

df_agg = df_agg.rename(columns={'mean': 'points'})
df_agg = df_agg.reset_index()
df_agg = df_agg[df_agg['count'] > 2].sort_values('points', ascending=False)
df_agg = df_agg.round(1)
df_agg = df_agg.reset_index(drop=True)

# join position and team info

info = pd.read_sql('select * from draft_fantasy_sharks', con)
info = info[['name', 'position', 'team']]
df = pd.merge(info, df_agg, on='name')

# value over replacement

pool_size = 14
roster = {
    'QB': 1,
    'WR': 4,
    'RB': 4,
    'TE': 1
}

head = int(sum(list(roster.values())) * pool_size * 2)
df['replacement'] = np.nan
for position, slots in roster.items():
    replacement = round(
        df[df['position'] == position]
        .reset_index(drop=True)
        .sort_values('points', ascending=False)
        .loc[:(slots * pool_size)]
        ['points']
        .mean()
    )
    df.loc[df['position'] == position, ['replacement']] = replacement

df['value_over_replacement'] = df['points'] - df['replacement']
df = df.sort_values('value_over_replacement', ascending=False).reset_index()

# dump

df.to_sql('value_over_replacement', con, if_exists='replace', index=False)
df.to_csv('value_over_replacement.csv', index=False)
