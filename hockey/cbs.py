import sqlite3
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

from hockey.utils import CATEGORIES

def _create_urls():
    positions = ['C', 'RW', 'LW', 'D', 'G']
    urls = []
    for position in positions:
        url = ('https://www.cbssports.com/fantasy/hockey/stats/sortable/points/'
        f'{position}/standard/projections/2018/ytd')
        urls.append(url)
    return urls

def _scrape_one(url):
    response = requests.get(url, params={'print_rows': 9999})
    table = '<table class="data compact"'
    df = pd.read_html(table + re.findall(f'{table}(.*)', response.text)[0])[0]
    df.columns = list(df.iloc[1].values)
    df = df.drop(df.index[[0, 1]])
    df['position'] = re.findall('points\/(.+?)\/standard', response.url)[0]
    return df

def _scrape(urls):
    df = pd.DataFrame()
    for url in urls:
        d = _scrape_one(url)
        df = df.append(d, sort=False)
    return df

def _transform(df):
    df = df.apply(pd.to_numeric, errors='ignore')
    df = df.reset_index(drop=True)
    df = df.rename(columns={
        'Player': 'name',
        'G': 'goals',
        'A': 'assists',
        'PTS': 'points',
        '+/-': 'plus_minus',
        'PIM': 'penalty_in_minutes',
        'W': 'wins',
        'SO': 'shutouts',
        'GAA': 'goals_against_average',
        'S': 'saves',
        'SPCT': 'save_percentage'})
    df[['name', 'team']] = df['name'].str.split(',\s', n=1, expand=True)
    df['powerplay_points'] = None
    df['games'] = None
    df['hits'] = None
    df['blocks'] = None
    df['shots_on_goal'] = None
    df['season'] = '2018-19'
    df['rank'] = None
    columns = ['season', 'rank', 'name', 'team', 'position', 'games']
    columns.extend(CATEGORIES)
    df = df[columns]
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df['source'] = 'CBS'
    df['fetched_at'] = pd.Timestamp('now')
    return df

def load():
    urls = _create_urls()
    raw = _scrape(urls)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('hockey/hockey.db')
    df = load()
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
