import sqlite3
from itertools import chain, cycle

import pandas as pd

con = sqlite3.connect('data/fantasy.db')
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

pd.read_sql(f'''
    select
    *
    from points
    where
    position = 'DEF' and
    season = {season} and
    week = {week}
    ''', con)
