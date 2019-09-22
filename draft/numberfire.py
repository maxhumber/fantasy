import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape(position):
    url = f'https://www.numberfire.com/nhl/fantasy/yearly-projections/{position}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('table', {'class':'projection-table'})
    names = pd.read_html(str(tables[0]))[0]
    data = pd.read_html(str(tables[1]))[0]
    df = pd.concat([names, data], axis=1)
    return df

df = pd.DataFrame()
for position in ['skaters', 'goalies']:
    df = df.append(scrape(position))

df = df.reset_index(drop=True)
column_mappings = {
    'Player': 'name',
    'G': 'goals',
    'A': 'assists',
    '+/-': 'plus_minus',
    'PPA': 'powerplay_assists',
    'PPG': 'powerplay_goals',
    'Shots': 'shots_on_goal',
    'Win': 'wins',
    'GAA': 'goals_against_average',
    'SV': 'saves',
    'SV%': 'save_percentage'
}
df = df.rename(columns=column_mappings)
df = df[column_mappings.values()]

df2 = df.copy()

df['team_pos'] = df['name'].apply(lambda x: x.split('(')[1].replace(')', '').split(' ,'))
df['name'] = df['name'].apply(lambda x: re.split("\s[A-Z]\.", x)[0])
df['powerplay_points'] = df['powerplay_assists'] + df['powerplay_goals']
df['save_percentage'] = df['save_percentage'].str.replace('%', '')
df['hits'] = None
df['blocks'] = None
df['shutouts'] = None
df['source'] = 'numberFire'
df['fetched_at'] = pd.Timestamp('now')

df.head(2)

    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric)
    df = df[['season', 'name', 'team', 'position', 'games', 'goals', 'assists',
           'plus_minus', 'powerplay_points', 'shots_on_goal', 'hits', 'blocks',
           'wins', 'goals_against_average', 'saves', 'save_percentage', 'shutouts',
           'source', 'fetched_at']]
    return df
