from itertools import chain, cycle
import pandas as pd

def snake(lower, upper):
    return cycle(chain(range(lower, upper + 1), range(upper, lower - 1, -1)))

teams = 14
slots = 10
s = snake(1, teams)
picks = teams * slots

df = pd.DataFrame([next(s) for _ in range(picks)])
df = df.reset_index()
df = df.rename(columns={'index': 'pick', 0: 'team'})
df['pick'] = df.pick + 1
df['round'] = (df.pick // teams) + 1

df[df['team'] == 2]

#
