import sqlite3
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

from hockey.utils import CATEGORIES

BASE_URL = 'http://www.numberfire.com/nhl/fantasy/yearly-projections'

def _scrape_one(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.findAll('span', {'class': 'abbrev'}):
        s.extract()
    names = pd.read_html(str(soup.findAll('table')[0]))[0]
    data = pd.read_html(str(soup.findAll('table')[1]))[0]
    df = pd.concat([names, data], axis=1)
    return df

def _scrape(urls):
    df = pd.DataFrame()
    for url in urls:
        d = _scrape_one(url)
        df = df.append(d, sort=False)
    return df

def _transform(df):
    df = df.reset_index(drop=True)
    df.columns = [c.lower() for c in df.columns]
    df[['name', 'position']] = df['player'].str.split('\s\s\(', n=1, expand=True)
    df[['position', 'team']] = df['position'].str.replace('\)', '').str.split(', ', n=1, expand=True)
    df['powerplay_points'] = df['ppa'] + df['ppa']
    df = df.rename(columns={
        '+/-': 'plus_minus',
        'a': 'assists',
        'g': 'goals',
        'gaa': 'goals_against_average',
        'sv': 'saves',
        'sv%': 'save_percentage',
        'win': 'wins',
        'shots': 'shots_on_goal',
        'w': 'wins'})
    df['save_percentage'] = df['save_percentage'].str.replace('%', '')
    df['hits'] = None
    df['blocks'] = None
    df['shutouts'] = None
    df['season'] = '2018-19'
    df['source'] = 'numberFire'
    df['fetched_at'] = pd.Timestamp('now')
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric)
    df = df[['season', 'name', 'team', 'position', 'games', 'goals', 'assists',
           'plus_minus', 'powerplay_points', 'shots_on_goal', 'hits', 'blocks',
           'wins', 'goals_against_average', 'saves', 'save_percentage', 'shutouts',
           'source', 'fetched_at']]
    return df

def load():
    urls = [BASE_URL + c for c in ['/goalies', '/skaters']]
    raw = _scrape(urls)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    cur = con.cursor()
    df = load()
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
