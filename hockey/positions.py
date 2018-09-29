import sqlite3
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
import bleach

url = 'https://www.nhl.com/news/fantasy-hockey-top-250-rankings-players-2018-19/c-281505474'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
soup = soup.find_all('p')
soup = [s for s in soup if 'C, EDM' in str(s)][0]

players = str(soup).split('<br/>')
players = [bleach.clean(player, tags=[], strip=True) for player in players]

df = pd.DataFrame(players)
df[['rank', 'name']] = df[0].str.split('. ', n=1, expand=True)
df[['name', 'position', 'team']] = df['name'].str.split(', ', n=2, expand=True)
df = df[['name', 'position']]

df[['main', 'secondary', 'tertiary']] = df['position'].str.split('/', n=2, expand=True)
df = pd.melt(df,
    id_vars=['name'], value_vars=['main', 'secondary', 'tertiary'],
    var_name='type', value_name='position')
df.loc[df['type'] != 'main', 'type'] = 'alternate'
df = df.dropna()
df = df.sort_values('name')
df['season'] = '2018-19'
df['source'] = 'NHL.com'
df['fetched_at'] = pd.Timestamp('now')

if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    df.to_sql('positions', con, if_exists='replace', index=False)
    con.commit()
    con.close()
