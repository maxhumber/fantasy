import sqlite3
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler

from hockey.utils import CATEGORIES

pd.options.display.max_rows = 50

con = sqlite3.connect('hockey/hockey.db')

def load_data(season='2018-19'):
    df = pd.read_sql(f'''
        select
        *
        from projections
        where season = '{season}'
        ''', con)
    # GAA is a bad thing, need to reverse
    df['goals_against_average'] = -df['goals_against_average']
    # merge different sources
    df = df.groupby(['season', 'name', 'position'])[CATEGORIES].mean().reset_index()
    return df

def calculate_vor(df, pool_size=10, starters={'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}):
    df = df.copy()
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

def scale_categories(df):
    df = df.copy()
    df[CATEGORIES] = (
        df
        .groupby('position')
        [CATEGORIES]
        .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    ).fillna(0)
    return df

def scale(x, out_range=[0.80, 1]):
    domain = np.min(x), np.max(x)
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2

def mod_categories(df, out_range=[0.80, 1]):
    df = df.copy()
    bias = pd.read_sql('select * from bias where feature not like "position%"', con)
    bias['mod'] = bias[['coef']].apply(lambda x: scale(x, out_range))
    bias = bias[['feature', 'mod']]
    bias = bias.set_index('feature').iloc[:,0]
    df[list(bias.keys())] *= bias
    return df

df = load_data()
pool_size = 10
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}
vor = calculate_vor(df, pool_size, starters)
cat = scale_categories(vor)
mod = mod_categories(cat)

name = 'Viktor Arvidsson'
df[df['name'] == name]
vor[vor['name'] == name]
cat[cat['name'] == name]
mod[mod['name'] == name]

df = mod
df['cat_score'] = df[CATEGORIES].sum(axis=1)
df = df.sort_values('cat_score', ascending=False)

players = sum(starters.values())
skaters = sum([value for key, value in starters.items() if key != 'G'])
goalies = players - skaters

df['cat_score'] = df['cat_score'] / players
df['cat_score_mod'] = np.where(df['position'] == 'G', df['cat_score'] / 2, df['cat_score'] / 10)
df = df.sort_values('cat_score_mod', ascending=False)

category = 'cat_score_mod'
for position, slots in starters.items():
    replacement = (
        df[df['position'] == position]
        .sort_values(category, ascending=False)
        .head(slots * pool_size)
        [category]
        .mean()
    )
    df.loc[df['position'] == position, category] = df[category] - replacement

df = df.sort_values(category, ascending=False)
df.to_csv('hockey/list.csv', index=False)
