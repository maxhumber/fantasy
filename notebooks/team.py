import sqlite3
from itertools import chain, cycle
import pandas as pd

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

df = pd.read_sql('select name, position, adp from draft where season = 2018', con)
df = df.dropna().sort_values('adp')



class Player:
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __repr__(self):
        return f"Player('{self.name}', '{self.position}')"

players = [Player(row['name'], row['position']) for index, row in df.iterrows()]

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

    def add_player(self, player):
        self.players.append(player)

phantasy = Team('pantasy')
phantasy.add_player(players[2-1])
phantasy.add_player(players[19-1])
phantasy.add_player(players[22-1])
phantasy.add_player(players[39-1])
Counter([p.position for p in phantasy.players])



def snake(lower, upper):
    return cycle(chain(range(lower, upper + 1), range(upper, lower - 1, -1)))

teams = 10
slots = 10
s = snake(1, teams)
picks = teams * slots
df = pd.DataFrame([next(s) for _ in range(picks)])
df = df.reset_index()
df = df.rename(columns={'index': 'pick', 0: 'team'})
df['pick'] = df.pick + 1
df['round'] = ((df.pick + 1) // teams) + 1
team_2 = df[df['team'] == 2]




players[2]
players



from collections import Counter
starters = ['QB'] + ['WR'] * 2 + ['RB'] * 3 + ['FLEX'] * 3 + ['TE']
Counter(starters)

class Team:


allowed_flex_positions = ['RB', 'TE', 'WR']
maximum_players = 18
starting_positions = ['K', 'D', 'FLEX', 'QB', 'RB', 'RB', 'TE', 'WR', 'WR']
weeks = list(range(1, 17))
