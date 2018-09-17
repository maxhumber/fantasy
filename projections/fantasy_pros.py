import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd

from utils.week import week
from utils.fuzzy import fuzzy_lookup

URL = 'https://www.fantasypros.com/nfl/projections/'

def _scrape(week, season=2018):
    df = pd.DataFrame()
    positions = ['qb', 'rb', 'wr', 'te', 'k', 'dst']
    for p in positions:
        url = f'{URL}{p}.php?week={week}'
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
        d['Position'] = p.upper()
        df = df.append(d)
    df['season'] = season
    df['week'] = week
    return df

def _transform(df):
    df = df.reset_index(drop=True)
    df['Team'] = df.Player.str.extract('\s(\w+)$')
    df.loc[df['Position'] != 'dst', 'Player'] = df['Player'].str.replace('\s(\w+)$', '')
    df.columns = [column.lower() for column in df.columns]
    df = df.rename(columns={'fpts': 'points', 'player': 'name'})
    df.loc[df['position'] == 'DST', 'position'] = 'DEF'
    df.loc[df['position'] == 'DEF', 'team'] = None
    df['name'] = df.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)
    # can't distinguish between NY and LA teams
    df = df[~df['name'].isin(['New York Giants', 'Los Angeles Rams'])]
    df['opponent'] = None
    df['source'] = 'Fantasy Pros'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'season', 'source', 'fetched_at']]
    return df

def load(week, season=2018):
    assert type(week) == int
    raw = _scrape(week, season)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
