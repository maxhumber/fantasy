import sqlite3
import flask
import pandas as pd
import numpy as np

pd.options.display.max_rows = 999  # for development

# load data from database

con = sqlite3.connect('nfl.db')
cur = con.cursor()

# vorp calculation dependant on pool size

def calculate_vorp(pool_size, roster):
    head = int(sum(list(roster.values())) * pool_size * 2)
    df = pd.read_sql('select * from stats', con)
    df['replacement'] = np.nan
    for position, slots in roster.items():
        replacement = round(
            df[df['pos'] == position]
            .reset_index(drop=True)
            .sort_values('points', ascending=False)
            .loc[:(slots * pool_size)]
            ['points']
            .mean()
        )
        df.loc[df['pos'] == position, ['replacement']] = replacement
    df['vorp'] = df['points'] - df['replacement']
    df = df.sort_values('vorp', ascending=False).reset_index()
    df = df.head(head)
    df = df.rename(columns={'index': 'old_rank'})
    df['old_rank'] = df['old_rank'] + 1
    df = df.drop('replacement', axis=1)
    return df

# specific

pool_size = 16
roster = {
    'QB': 1,
    'WR': 3,
    'RB': 2,
    'TE': 1,
    'K': 1,
    'DEF': 1
}

df = calculate_vorp(pool_size, roster)
df.head(20)
df[df['pos'] == 'QB']
#
