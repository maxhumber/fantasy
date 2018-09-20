import sqlite3

import pandas as pd

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

team = 'phantasy'
week = 3
season = 2018

def read_waiver_wire(team, week, season):
    sql = f'''
    select
    team,
    name,
    position,
    points
    from (
        select
        name,
        position,
        week,
        season,
        avg(points) as points
        from projections
        where
        week = 3 and
        season = 2018 and
        strftime('%Y-%m-%d', fetched_at) = (select max(strftime('%Y-%m-%d', fetched_at)) from projections)
        group by 1, 2, 3, 4
        having count(*) > 1
    ) projections
    left join (
        select
        name,
        position,
        team
        from rosters
        where
        strftime('%Y-%m-%d', fetched_at) = (select max(strftime('%Y-%m-%d', fetched_at)) from rosters)
    ) as rosters using (name, position)
    where
    team is null or
    team = 'phantasy'
    order by points desc
    '''
    return pd.read_sql(sql, con)

df = df[['team', 'name', 'position', 'points']]
