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

def calculate_score(df, starters, pool_size):
    score_name = 'cat_score'
    df = df.copy()
    df[score_name] = df[CATEGORIES].sum(axis=1)

    players = sum(starters.values())
    skaters = sum([value for key, value in starters.items() if key != 'G'])
    goalies = players - skaters

    df[score_name] = df['cat_score'] / players
    df[score_name] = np.where(df['position'] == 'G', df[score_name] / 2, df[score_name] / 10)

    for position, slots in starters.items():
        replacement = (
            df[df['position'] == position]
            .sort_values(score_name, ascending=False)
            .head(slots * pool_size)
            [score_name]
            .mean()
        )
        df.loc[df['position'] == position, score_name] = df[score_name] - replacement

    df['custom_rank'] = df[score_name].rank(method='average', ascending=False)

    return df[['name', 'custom_rank', score_name]].sort_values(score_name, ascending=False)

df = load_data()
pool_size = 10
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}
vor = calculate_vor(df, pool_size, starters)
cat = scale_categories(vor)
mod = mod_categories(cat)
scores = calculate_score(mod, starters, pool_size)

half = pd.merge(vor, scores, how='left', on='name')
ranks = pd.read_sql('select name, rank from ranks', con)
full = pd.merge(half, ranks, how='left', on='name')
full['rank_arbitrage'] = full['rank'] - full['custom_rank']
full = full.sort_values('custom_rank')

name = 'Viktor Arvidsson'
df[df['name'] == name]
vor[vor['name'] == name]
cat[cat['name'] == name]
mod[mod['name'] == name]

df = full
df.to_csv('hockey/list.csv', index=False)
