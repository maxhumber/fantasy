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

projections = pd.read_sql(f'''
    select
    *
    from projections
    where
    position = 'DEF' and
    season = {season} and
    week = {week}
    ''', con)

available = projections[~projections['name'].isin(taken)]

stream = available.sort_values('points', ascending=False).head(3).sample(frac=1).head(1)

points = pd.read_sql(f'''
    select
    name,
    position,
    week,
    season,
    points
    from points
    where
    position = 'DEF' and
    season = {season} and
    week = {week}
    ''', con)

points[~points['name'].isin(taken)]






#
