import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup
from utils.week import week

URL = 'https://www.fantasypros.com/nfl/projections/'

def _scrape(week):
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
    return df

def _transform(df, week):
    df = df.reset_index(drop=True)
    df['Team'] = df.Player.str.extract('\s(\w+)$')
    df.loc[df['Position'] != 'dst', 'Player'] = (
        df[df['Position'] != 'dst']['Player'].str.replace('\s(\w+)$', '')
    )
    df.columns = ['name', 'points', 'position', 'team']
    df.loc[df['position'] == 'DST', 'position'] = 'DEF'
    df.loc[df['position'] == 'DEF', 'team'] = None
    df['opponent'] = None
    df['week'] = week
    df['source'] = 'Fantasy Pros'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    return df

def load(week):
    raw = _scrape(week)
    clean = _transform(raw, week)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
