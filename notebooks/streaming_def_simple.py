import sqlite3
from itertools import chain, cycle

import pandas as pd

con = sqlite3.connect('data/football.db')
cur = con.cursor()

teams = 10
season = 2017
week = 1

taken = list(pd.read_sql(f'''
    select
    *
    from draft
    where
    position = 'DEF' and
    season = {season}
    limit {teams}
    ''', con)['name'].values)

all = pd.read_sql(f'''
    select
    projections.name,
    projections.week,
    projections.season,
    projections.points as projection,
    points.points
    from projections
    left join points using (name, position, season, week)
    where
    position = 'DEF' and
    season = {season} and
    week = {week}
    order by week, projections.points desc
    ''', con)

all[all['name'].isin(taken)






df = pd.read_sql(f'''
    select
    projections.name,
    projections.week,
    projections.season,
    projections.points as projection,
    points.points
    from projections
    left join points using (name, position, season, week)
    where
    position = 'DEF' and
    season = {season} and
    week = {week}
    order by week, projections.points desc
    ''', con)

df = df.groupby('week').first().reset_index()
streaming = df['points'].sum()

#
