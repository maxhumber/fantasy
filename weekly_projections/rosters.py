import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import re
from week import week
from fuzzywuzzy import process, fuzz
from fuzzy_defence import fuzzy_defence

con = sqlite3.connect('projections.db')
cur = con.cursor()

players = pd.read_sql('select * from players', con)

def fuzzy_player(player, position):
    choices = list(players[players['position'] == position]['name'].values)
    try:
        match = process.extract(player, choices=choices, scorer=fuzz.partial_token_sort_ratio)[0]
        if match[1] > 75:
            return match[0]
        else:
            return player
    except IndexError:
        return player

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
df['name'] = df.apply(lambda row: fuzzy_player(row['name'], row['position']), axis=1)
df.loc[df['position'] == 'DEF', 'name'] = (
    df['name'].apply(lambda team: fuzzy_defence(team))
)
df['week'] = week
df['fetched_at'] = pd.Timestamp('now')
df.to_sql('rosters', con, if_exists='replace', index=False)
