import sqlite3
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

from hockey.utils import CATEGORIES

URL = 'https://www.dailyfaceoff.com/daily-hockey-player-projections/'

def _quick_table(table):
    df = pd.read_html(str(table))[0]
    df.columns = list(df.iloc[0].values)
    df['name'] = df.iloc[0, 0]
    df = df.drop(df.index[0])
    df = df.drop(df.columns[[0]], axis=1)
    return df

def _scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('table')
    df = pd.DataFrame()
    for table in tables:
        d = _quick_table(table)
        df = df.append(d)
    return df

def _transform(df):
    df = df.apply(pd.to_numeric, errors='ignore')
    # rotten apple
    df.loc[df['name'].str.contains('168'), 'name'] = '168. Ryan McDonagh, TB – D'
    df[['rank', 'name']] = df['name'].str.split('.\s', n=1, expand=True)
    df[['name', 'team_pos']] = df['name'].str.split(',\s', n=1, expand=True)
    df[['team', 'position']] = df['team_pos'].str.split('\s–\s', n=1, expand=True)
    df = df.reset_index(drop=True)
    df.loc[df['position'] != 'G', 'goals'] = df['G/W']
    df.loc[df['position'] == 'G', 'wins'] = df['G/W']
    df.loc[df['position'] != 'G', 'assists'] = df['A/GAA']
    df.loc[df['position'] == 'G', 'goals_against_average'] = df['A/GAA']
    df.loc[df['position'] != 'G', 'points'] = df['Pts/SV%']
    df.loc[df['position'] == 'G', 'save_percentage'] = df['Pts/SV%']
    df = df.rename(columns={
        'Year': 'season',
        'GP': 'games',
        'SO': 'shutouts',
        'SOG': 'shots_on_goal',
        'PIMS': 'penalty_in_minutes',
        'PPG': 'powerplay_goals',
        'PPA': 'powerplay_assists',
        'PPP': 'powerplay_points',
        'Hit': 'hits',
        'BLK': 'blocks'
    })
    df['shutouts'] = pd.to_numeric(df['shutouts'], errors='coerce')
    df.loc[df['season'] == '2017-18', 'rank'] = None
    df['plus_minus'] = None
    df['saves'] = None
    columns = ['season', 'rank', 'name', 'team', 'position', 'games']
    columns.extend(CATEGORIES)
    df = df[columns]
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df['source'] = 'Daily Face Off'
    df['fetched_at'] = pd.Timestamp('now')
    return df

def load():
    raw = _scrape()
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('hockey/hockey.db')
    df = load()
    df.to_sql('projections', con, if_exists='replace', index=False)
    con.commit()
    con.close()
