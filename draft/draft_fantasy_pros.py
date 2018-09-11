# Fantasy Pros
# https://www.fantasypros.com/nfl/projections/qb.php?week=draft

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# fetch

df = pd.DataFrame()
positions = ['qb', 'rb', 'wr', 'te', 'k', 'dst']
for p in positions:
    url = f'https://www.fantasypros.com/nfl/projections/{p}.php?week=draft'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    d = pd.read_html(str(soup.findAll('table')[0]))[0]
    d = d.T.reset_index().T
    if p in ('qb', 'rb', 'wr', 'te'):
        d.columns = list(d.iloc[1].values)
        d = d.drop(d.index[[0, 1]])
    else:
        d.columns = list(d.iloc[0].values)
        d = d.drop(d.index[0])
    d = d[['Player', 'FPTS']]
    d['Position'] = p
    df = df.append(d)

# clean

df = df.reset_index(drop=True)
df['Team'] = df.Player.str.extract('\s(\w+)$')
df.loc[df['Position'] != 'dst', 'Player'] = (
    df[df['Position'] != 'dst']['Player'].str.replace('\s(\w+)$', '')
)

df.columns = ['name', 'points', 'position', 'team']
df.loc[df['position'] == 'dst', 'position'] = 'def'
df['position'] = df['position'].str.upper()
df.loc[df['position'] == 'DEF', 'team'] = None
df = df[['name', 'position', 'team', 'points']]

# dump

df.to_sql('draft_fantasy_pros', con, if_exists='replace', index=False)
