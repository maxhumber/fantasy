import sqlite3
from itertools import chain, cycle
import pandas as pd
from collections import Counter

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

df = pd.read_sql('select name, position, adp from draft where season = 2018', con)
df = df.dropna().sort_values('adp')

con.commit()

class Player:

    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __repr__(self):
        return f"Player('{self.name}', '{self.position}')"

class Team:

    SLOTS = {'QB': 1, 'WR': 3, 'RB': 2, 'TE': 1, 'K': 1, 'DEF': 1}

    def __init__(self, name):
        self.name = name
        self.players = []

    def okay_to_draft(self, player):
        position = player.position
        current = Counter([p.position for p in self.players])
        return current[position] < SLOTS[position]

    def add_player(self, player):
        self.players.append(player)

    def __repr__(self):
        return f"Team('{self.name}')"

players = [Player(row['name'], row['position']) for index, row in df.iterrows()]
teams = 14
slots = 10
league = {i: Team(i) for i in range(1, teams + 1)}
snake = generate_snake(1, teams)

for i in range(teams * slots):
    pick = next(snake)
    print(pick)
    team = league[pick]
    j = 0
    if team.okay_to_draft(players[j]):
        team.add_player(players.pop(j))
    else:
        continue


league[1].players
league[2].players
league[3].players
league[4].players



phantasy = Team('phantasy')
players = [Player(row['name'], row['position']) for index, row in df.iterrows()]
phantasy.add_player(players.pop(0))
phantasy.players

phantasy.okay_to_draft(players[0])
phantasy.add_player(players.pop(0))
players



[players.pop(0) for i in range(10)]

phantasy.players
phantasy.okay_to_draft(players[0])
players


phantasy = Team('phantasy')
phantasy.add_player(players[2-1])
phantasy.add_player(players[19-1])
phantasy.add_player(players[22-1])
phantasy.add_player(players[39-1])
phantasy.players









def generate_snake(lower, upper):
    return cycle(chain(range(lower, upper + 1), range(upper, lower - 1, -1)))

teams = 10
slots = 10
s = snake(1, teams)
next(s)

picks = teams * slots
df = pd.DataFrame([next(s) for _ in range(picks)])
df = df.reset_index()
df = df.rename(columns={'index': 'pick', 0: 'team'})
df['pick'] = df.pick + 1
df['round'] = ((df.pick + 1) // teams) + 1
team_2 = df[df['team'] == 2]


from collections import Counter
starters = ['QB'] + ['WR'] * 2 + ['RB'] * 3 + ['FLEX'] * 3 + ['TE']
Counter(starters)

class Team:


allowed_flex_positions = ['RB', 'TE', 'WR']
maximum_players = 18
starting_positions = ['K', 'D', 'FLEX', 'QB', 'RB', 'RB', 'TE', 'WR', 'WR']
weeks = list(range(1, 17))
