import sqlite3
import pandas as pd
import numpy as np

from hockey.utils import CATEGORIES

pd.options.display.max_rows = 999

con = sqlite3.connect('hockey/hockey.db')
df = pd.read_sql('select * from stats where season = "2018-19"', con)

# GAA is a bad thing, need to reverse
df['goals_against_average'] = -df['goals_against_average']
# merge different sources
df = df.groupby(['season', 'name', 'position'])[CATEGORIES].mean().reset_index()

pool_size = 10
roster = {
    'C': 2,
    'LW': 2,
    'RW': 2,
    'D': 4,
    'G': 2
}

# position = 'G'
# df = df[df['position'] == 'G'].dropna(axis=1)
# category = 'goals_against_average'

# value abpve replacement

for position, slots in roster.items():
    for category in CATEGORIES:
        try:
            replacement = (
                df[df['position'] == position]
                .sort_values(category, ascending=False)
                .head(slots * pool_size)
                [category]
                .mean()
            )
            df.loc[df['position'] == position, category] = df[category] - replacement
        except ValueError:
            pass
        except KeyError:
            pass

# df[df['position'] == 'G'].dropna(axis=1, thresh=10)
df
# scale 0-1
df.groupby('position')[CATEGORIES].apply(lambda x: (x - x.min()) / (x.max() - x.min())).sum(axis=1)
df
df['idk'] = df[CATEGORIES].apply(lambda x: (x - x.min()) / (x.max() - x.min())).sum(axis=1)
# df['idk'] = df[CATEGORIES].sum(axis=1)
df = df.sort_values('idk', ascending=False)

df[df['position'] == 'G'].dropna(axis=1)
