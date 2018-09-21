import sqlite3
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler

from hockey.utils import CATEGORIES

pd.options.display.max_rows = 50

con = sqlite3.connect('hockey/hockey.db')

def load_data(season='2018-19'):
    df = pd.read_sql(f'''
        select
        *
        from stats
        where season = '{season}'
        ''', con)
    # GAA is a bad thing, need to reverse
    df['goals_against_average'] = -df['goals_against_average']
    # merge different sources
    df = df.groupby(['season', 'name', 'position'])[CATEGORIES].mean().reset_index()
    return df

df = load_data()

def calculate_vor(df, pool_size=10, starters={'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}):
    for position, slots in starters.items():
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
    return df

pool_size = 10
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}
vor = calculate_vor(df, pool_size, starters)

def scale_categories(df):
    df[CATEGORIES] = (
        df
        .groupby('position')
        [CATEGORIES]
        .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    ).fillna(0)
    return df

cat = scale_categories(vor)

players = sum(starters.values())
skaters = sum([value for key, value in starters.items() if key != 'G'])
goalies = players - skaters

df = cat

df['cat_score'] = df[CATEGORIES].sum(axis=1)
df.sort_values('cat_score', ascending=False)

df['cat_score'] = df['cat_score'] / players
df['cat_score_mod'] = np.where(df['position'] == 'G', df['cat_score'] / 2, df['cat_score'] / 10)
df = df.sort_values('cat_score_mod', ascending=False)
df.to_csv('hockey/list.csv', index=False)
