import sqlite3
from itertools import chain, cycle

import pandas as pd
import altair as alt

con = sqlite3.connect('data/football.db')
cur = con.cursor()

season = 2017

breakout_week_1 = pd.read_sql(f'''
    select
    *
    from (
        select
        name,
        points.position,
        week,
        season,
        adp,
        ifnull(projections.points, 0) as projection,
        points.points,
        points.points - ifnull(projections.points, 0) as delta
        from points
        left join projections using (name, position, week, season)
        left join draft using (name, season)
        where
        week = 1 and
        season = {season} and
        points.position in ('WR', 'RB') and
        (adp is null or adp >= 150)
    ) breakouts
    where delta > 5
    order by season, delta desc
    ''', con)

players = [f"'{name}'" for name in breakout_week_1['name'].values]

full_season = pd.read_sql(f'''
    select
    name,
    position,
    week,
    season,
    points
    from points
    where
    season = {season} and
    name in ({', '.join(players)})
    order by name, week
    ''', con)

df1 = full_season
df1 = df1.set_index(['name', 'position', 'season', 'week'])
df1 = df1.unstack().fillna(0).stack().reset_index()

selector = alt.selection_single(empty='all', fields=['name'])

(alt.Chart(df1)
    .properties(background='white', height=400, width=600)
    .mark_line()
    .encode(x='week', y='points', color='name', tooltip=['name'])
    .add_selection(selector)
    .transform_filter(selector)
    .interactive()
)

#
