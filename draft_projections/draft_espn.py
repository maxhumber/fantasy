# ESPN
# http://games.espn.com/ffl/tools/projections?&startIndex=0

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# fetch

URL = 'http://games.espn.com/ffl/tools/projections'

df = pd.DataFrame()
for i in range(0, 400, 40):
    payload = {'startIndex': i}
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    d = pd.read_html(str(soup.findAll('table')[0]))[0]
    d.columns = list(d.iloc[2].values)
    d = d.drop(d.index[0:3])
    df = df.append(d)

# clean

df = df[['PLAYER, TEAM POS', 'PTS']]
df = df.reset_index(drop=True)
df[['name', 'pos_team']] = df['PLAYER, TEAM POS'].str.split(', ', expand=True)
df[['team', 'position']] = df['pos_team'].str.split('\\s', expand=True).iloc[:, [0, 1]]
df = df.rename(columns={'PTS': 'points'})
df = df[['name', 'position', 'team', 'points']]
df['name'] = df['name'].str.replace('*', '')
df['name'] = df['name'].str.replace('\\sD/ST\\sD/ST', '')

# dump

df.to_sql('draft_espn', con, if_exists='replace', index=False)
