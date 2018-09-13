import sqlite3
from itertools import chain, cycle

import pandas as pd

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

season = 2017

df = pd.read_sql(f'''
    select
    draft.name,
    def.position,
    def.season,
    def.points,
    round(draft.adp, 1) as adp
    from (
        select
        name,
        position,
        season,
        round(sum(points)) as points
        from points
        where position = 'DEF'
        group by 1, 2, 3
    ) def
    left join draft using (name, season)
    where season = {season} and
    adp is not null
    order by season, adp
    ''', con)

teams = 10
DEF = list(df[:teams]['name'].values)
DEF = [f"'{d}'" for d in DEF]

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
    name not in ({', '.join(DEF)}) and
    season = {season}
    order by week, projections.points desc
    ''', con)

df = df.groupby('week').first().reset_index()
streaming = df['points'].sum()







#
