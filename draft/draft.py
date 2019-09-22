import sqlite3
import pandas as pd
import numpy as np
from copy import deepcopy
from sklearn.preprocessing import StandardScaler, MinMaxScaler
# from sklearn.impute import SimpleImputer

from hockey.utils import CATEGORIES, scale

pd.options.display.max_rows = 50

con = sqlite3.connect('data/hockey.db')

season = '2018-19'

projections = pd.read_sql(f'''
    SELECT
        name,
        {', '.join(CATEGORIES)}
    FROM
        projections
    WHERE
        season = '{season}'
''', con)

positions = pd.read_sql(f'''
    SELECT
        name,
        type,
        position
    FROM
        positions
    WHERE
        season = '{season}'
''', con)

df = pd.merge(positions, projections, how='left', on='name')
df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
# GAA is a bad thing, need to reverse
df['goals_against_average'] = -df['goals_against_average']
# merge different sources
df = df.groupby(['name', 'position', 'type'])[CATEGORIES].mean().reset_index()

# pool particulars
pool_size = 10
starters = {'C': 2, 'LW': 2, 'RW': 2, 'D': 4, 'G': 2}

df[CATEGORIES] = (
    df
    [CATEGORIES]
    .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
)

bias = pd.read_sql('select * from bias where feature not like "position%"', con)
bias['mod'] = bias[['coef']].apply(lambda x: scale(x, (0.8, 1)))
bias = bias[['feature', 'mod']].set_index('feature').iloc[:,0]
df[list(bias.keys())] *= bias

# score calc
# scrap goals and shutouts from the score
cats = deepcopy(CATEGORIES)
cats.remove('goals')
cats.remove('shutouts')
df['score'] = df[cats].sum(axis=1)

players = sum(starters.values())
skaters = sum([value for key, value in starters.items() if key != 'G'])
goalies = players - skaters

df['score'] = df['score'] / players
df['score'] = np.where(df['position'] == 'G', df['score'] / goalies, df['score'] / skaters)

for position, slots in starters.items():
    replacement = (
        df[df['position'] == position]
        .sort_values('score', ascending=False)
        .head(slots * pool_size)
        ['score']
        .mean()
    )
    df.loc[df['position'] == position, 'score'] = df['score'] - replacement

# remove alternate positions now
df = df[df['type'] == 'main']
df = df.drop('type', axis=1)

# finish rank
df['score'] = df[['score']].apply(lambda x: scale(x, (0, 1)))
df['my_rank'] = df['score'].rank(method='average', ascending=False)
df = df.sort_values('my_rank')
df['position_rank'] = df.groupby(['position'])['score'].rank(ascending=False)

adp = pd.read_sql('''
    SELECT
        name,
        CAST(yahoo AS numeric) as adp
    FROM
        positions
        LEFT JOIN orders USING (name)
    WHERE
        positions.type = 'main'
        AND yahoo IS NOT NULL
    ORDER BY
        2
    ''', con)

df = pd.merge(df, adp, how='left', on='name')
df['arbitrage'] = df['adp'] - df['my_rank']
df['round'] = (df['adp'] / pool_size) + 1
# df = df.drop('position', axis=1)

multi = positions[['name', 'position']].groupby('name').agg(lambda x: '/'.join(x.unique())).reset_index()
multi.columns = ['name', 'multi']
df = pd.merge(df, multi, how='left', on='name')

df = df[['score', 'round', 'arbitrage', 'adp', 'my_rank', 'name', 'position', 'multi', 'position_rank'] + CATEGORIES]
df.to_csv('hockey/draft/list.csv', index=False)
