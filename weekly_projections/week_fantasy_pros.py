import requests
import pandas as pd
from bs4 import BeautifulSoup
from week import week
import sqlite3

con = sqlite3.connect('projections.db')
cur = con.cursor()

def scrape():
    df = pd.DataFrame()
    positions = ['qb', 'rb', 'wr', 'te', 'k', 'dst']
    for p in positions:
        url = f'https://www.fantasypros.com/nfl/projections/{p}.php?week={week}'
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

def etl():
    df = scrape()
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
    df.to_sql(f'projections', con, if_exists='append', index=False)

if __name__ == '__main__':
    etl()
    print('Success!')
