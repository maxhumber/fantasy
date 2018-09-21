import sqlite3
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler

from hockey.utils import CATEGORIES

pd.options.display.max_rows = 50

con = sqlite3.connect('hockey/hockey.db')

def scale(x, out_range=[0.80, 1]):
    domain = np.min(x), np.max(x)
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2

def load_data(season='2018-19'):
    df = pd.read_sql(f'''
        select
        name,
        coalesce(ranks.position, projections.position) as position,
        goals,
        assists,
        plus_minus,
        powerplay_points,
        shots_on_goal,
        hits,
        blocks,
        wins,
        goals_against_average,
        saves,
        save_percentage,
        shutouts,
        projections.source,
        projections.fetched_at
        from projections
        left join ranks using (name, season)
        where
        season = '{season}' and
        name in (
            select
            name
            from projections
            where season = '{season}'
            group by 1
            having count(*) > 1
        )
    ''', con)
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    # GAA is a bad thing, need to reverse
    df['goals_against_average'] = -df['goals_against_average']
    # merge different sources
    df = df.groupby(['name', 'position'])[CATEGORIES].mean().reset_index()
    return df

df = load_data()

pool_size = 10
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}

df[CATEGORIES] = (
    df
    [CATEGORIES]
    .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
).fillna(0)

bias = pd.read_sql('select * from bias where feature not like "position%"', con)
bias['mod'] = bias[['coef']].apply(lambda x: scale(x, (0.8, 1)))
bias = bias[['feature', 'mod']].set_index('feature').iloc[:,0]
df[list(bias.keys())] *= bias

df['score'] = df[CATEGORIES].sum(axis=1)

players = sum(starters.values())
skaters = sum([value for key, value in starters.items() if key != 'G'])
goalies = players - skaters

df['score'] = df['score'] / players
df['score'] = np.where(df['position'] == 'G', df['score'] / 2, df['score'] / 10)

for position, slots in starters.items():
    replacement = (
        df[df['position'] == position]
        .sort_values('score', ascending=False)
        .head(slots * pool_size)
        ['score']
        .mean()
    )
    df.loc[df['position'] == position, 'score'] = df['score'] - replacement

df['custom_rank'] = df['score'].rank(method='average', ascending=False)
df = df.sort_values('custom_rank')
ranks = pd.read_sql('select name, rank from ranks', con)
df = pd.merge(df, ranks, how='left', on='name')
df['rank_arbitrage'] = df['custom_rank'] - df['rank']
df.to_csv('hockey/list.csv', index=False)
