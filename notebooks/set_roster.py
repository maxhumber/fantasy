import sqlite3
from itertools import chain, cycle
import pandas as pd
from collections import Counter
import random

from fantasy.utils.week import week

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

team = 'phantasy'
week = 3
season = 2018

df = pd.read_sql(f'''
    select
    name,
    position,
    week,
    season,
    points,
    range
    from (
    	select
    	name,
    	position,
    	week,
    	season,
    	strftime('%Y-%m-%d', fetched_at) as fetched_at,
    	round(avg(points), 1) as points,
    	(round(min(points), 1) || '-' || round(max(points), 1)) as range,
    	count(*) as count
    	from projections
    	where
    	season = {season} and
    	week = {week} and
    	strftime('%Y-%m-%d', fetched_at) = (select max(strftime('%Y-%m-%d', fetched_at)) from projections)
    	group by 1, 2, 3, 4, 5
    	having count(*) > 1
    ) projections
    left join (
        select
        *
        from rosters
        where
        strftime('%Y-%m-%d', fetched_at) =
            (select max(strftime('%Y-%m-%d', fetched_at)) from rosters)
    ) as rosters using (name, position)
    where team = '{team}'
    order by points desc
''', con)

class Player:

    def __init__(self, name, position, points):
        self.name = name
        self.position = position
        self.points = points

    def __repr__(self):
        return f"Player('{self.name}', '{self.position}', {self.points})"

players = [Player(row['name'], row['position'], row['points']) for index, row in df.iterrows()]
random.shuffle(players)

remaining_players = sorted(players, key=lambda player: player.points, reverse=True)

positions = {
    'QB': 1,
    'RB': 2,
    'WR': 3,
    'TE': 1,
    'FLEX': 3,
    'K': 1,
    'DEF': 1
}
positions = [item for sublist in [[k]*v for k,v in positions.items()] for item in sublist]

starters = []
for position in positions:
    for i, player in enumerate(remaining_players):
        if player.position == position:
            starters.append(remaining_players.pop(i))
            break

flex = len([p for p in positions if p == 'FLEX'])
for i in range(flex):
    for j, player in enumerate(remaining_players):
        if player.position in ['WR', 'RB', 'TE']:
            starters.append(remaining_players.pop(j))
            break

players
starters
