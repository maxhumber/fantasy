import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import re
from week import week
from fuzzywuzzy import process, fuzz


ALPHABET = [chr(i) for i in range(ord('A'),ord('Z')+1)]
URL = 'https://www.footballdb.com/players/current.html'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

payloads = [{'letter': letter} for letter in ALPHABET]
https://www.footballdb.com/players/current.html?pos=WR

payload = {'pos': 'WR'}

payload = payloads[0]

response = requests.get(URL, params=payload, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
for s in soup.find_all(class_='td hidden-xs'):
    s.extract()
soup = soup.find_all('div', class_='td')

players = []
for s in soup:
    try:
        players.append(s.find('a')['title'])
    except TypeError:
        pass
    except KeyError:
        pass
pd.DataFrame({'name': players})






con = sqlite3.connect('projections.db')
cur = con.cursor()

position = 'QB'

players = (
    pd.read_sql(f'''
        select
        name,
        position
        from projections
        where
        source = 'Fantasy Sharks' and
        week = {week}
    ''', con)
)

def fuzzy_player(player, position):
    choices = list(players[players['position'] == position]['name'].values)
    return process.extract(player, choices=choices, scorer=fuzz.partial_ratio)[0][0]


league = 4319624
URL = f'http://fantasy.nfl.com/league/{league}/depthcharts'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'lxml')
df = pd.read_html(str(soup.findAll('table')[0]))[0]
df.columns = list(df.iloc[0].values)
df = df.drop(df.index[0])
df = pd.melt(df, id_vars=['Team'], var_name = 'position', value_name='players')
df['players'] = (
    df['players']
    .apply(
        lambda s: re.findall('[A-Z]\.\s[A-Z][a-z]+', s)
        if '.' in s
        else re.findall('([A-Z][a-z]*)', s)
    )
)
df = df.set_index(['Team', 'position'])
df = (df['players'].apply(pd.Series)
    .stack()
    .reset_index(level=2, drop=True)
    .to_frame('players')
)
df = df.reset_index().sort_values('Team', ascending=False)
df.columns = ['team', 'position', 'name']


player = 'C. Meredith'
position = 'WR'
choices = list(players[players['position'] == position]['name'].values)
process.extract(player, choices=choices, scorer=fuzz.partial_ratio)[0][0]

help(process.extract)

df['name2'] = df.apply(lambda row: fuzzy_player(row['name'], row['position']), axis=1)
df



df


df['week'] = week
df['fetched_at'] = pd.Timestamp('now')

df.to_sql('rosters', con, if_exists='replace', index=False)
