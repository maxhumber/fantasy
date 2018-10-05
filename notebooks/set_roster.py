import sqlite3
from itertools import chain, cycle
import pandas as pd
from collections import Counter
import random

from football.utils.week import week

POSITIONS = {
    'QB': 1,
    'RB': 2,
    'WR': 3,
    'TE': 1,
    'FLEX': 3,
    'K': 1,
    'DEF': 1
}

class Player:

    def __init__(self, name, position, points):
        self.name = name
        self.position = position
        self.points = points

    def __repr__(self):
        return f"Player('{self.name}', '{self.position}', {self.points})"

def read_projection_data(team, week, season):
    sql = f'''
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
    '''
    return pd.read_sql(sql, con)

def optimize_roster(team, week, season=2018, positions=POSITIONS):
    df = read_projection_data(team, week, season)

    players = [Player(row['name'], row['position'], row['points']) for index, row in df.iterrows()]
    remaining_players = sorted(players, key=lambda player: player.points, reverse=True)
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

    return starters

if __name__ == '__main__':
    con = sqlite3.connect('data/football.db')
    cur = con.cursor()
    starters = optimize_roster('phantasy', week)
    print('Starters:\n')
    print('\n'.join(str(starter) for starter in starters))
    print('\nPoints: ', round(sum([player.points for player in starters]), 1))
