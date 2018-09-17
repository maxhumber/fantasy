import sqlite3

import pandas as pd
import numpy as np

pd.options.display.max_rows = 999

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

# pull

sql = 'select * from draft where season = 2018'
df = pd.read_sql(sql, con)
df = df.infer_objects()
df['points'] = pd.to_numeric(df['points'])

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

df[['name', 'position', 'points', 'replacement', 'value_over_replacement']]
