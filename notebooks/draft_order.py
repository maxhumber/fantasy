import sqlite3
from itertools import chain, cycle

import pandas as pd

con = sqlite3.connect('data/football.db')
cur = con.cursor()

season = 2017

adp = pd.read_sql(f'''
    select
    name,
    stats.position,
    season,
    stats.points,
    adp
    from draft
    left join (
        select
        name,
        position,
        season,
        round(sum(points)) as points
        from points
        group by 1, 2, 3
    ) as stats using (name, season)
    where
    stats.points is not null and
    season = {season}
    order by season, adp
    ''', con)

def snake(lower, upper):
    return cycle(chain(range(lower, upper + 1), range(upper, lower - 1, -1)))

def dummy_draft(df, teams=10, slots=10):
    s = snake(1, teams)
    picks = teams * slots
    for index, row in adp.iterrows():
        df.loc[index, 'pick'] = index + 1
        df.loc[index, 'team'] = next(s)
    df['round'] = ((df.pick - 1) // teams) + 1
    df = df[df['pick'] <= picks]
    return df

draft = dummy_draft(adp)

draft.groupby('team')['points'].sum()
