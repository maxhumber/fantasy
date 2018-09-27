import sqlite3
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

from football.utils.week import week
from football.utils.fuzzy import fuzzy_apply

BASE_URL = 'http://www.numberfire.com/nfl/fantasy/'

def _create_urls(week):
    if week == 'all':
        URL = BASE_URL + 'remaining-projections'
    else:
        URL = BASE_URL + 'fantasy-football-projections'
    urls = [URL, URL + '/k', URL + '/d']
    return urls

def _scrape_one(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.findAll('span', {'class': 'abbrev'}):
        s.extract()
    names = pd.read_html(str(soup.findAll('table')[0]))[0]
    data = pd.read_html(str(soup.findAll('table')[1]))[0]
    df = pd.concat([names, data], axis=1)
    # handle remaining season projections
    if 'remaining' in url:
        df = df.iloc[:, 0:2]
        df.columns = ['name', 'points']
        # remove fake precision
        df['points'] = round(df['points'])
        df['week'] = 'all'
        df['season'] = 2018
        return df
    if url[-1] in ('k', 'd'):
        df = df.iloc[:, 0:4]
        df.columns = ['name', 'points', 'ci', 'opponent']
        df = df.drop('ci', axis=1)
    else:
        df = df.iloc[:, 0:3]
        df.columns = ['name', 'points', 'opponent']
    h2_week = str(soup.find(class_='projection-rankings__hed').find('h2'))
    h2_week = int(re.findall('Week\s(.*?)\sFantasy', h2_week)[0])
    df['week'] = h2_week
    # no support for other seasons
    df['season'] = 2018
    return df

def _scrape(urls):
    df = pd.DataFrame()
    for url in urls:
        d = _scrape_one(url)
        df = df.append(d)
    return df

def _transform(df):
    df = df.reset_index(drop=True)
    df[['name', 'position']] = df['name'].str.split('\s\s\(', n=1, expand=True)
    df[['position', 'team']] = df['position'].str.split(', ', n=1, expand=True)
    df['team'] = df['team'].str.replace(')', '')
    df['name'] = df['name'].str.replace('\sD/ST', '')
    df.loc[df['position'] == 'D', 'position'] = 'DEF'
    df = fuzzy_apply(df)
    df['source'] = 'numberFire'
    df['fetched_at'] = pd.Timestamp('now')
    if 'opponent' not in df:
        df['opponent'] = None
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'season', 'source', 'fetched_at']]
    return df

def load(week, season=2018):
    urls = _create_urls(week)
    raw = _scrape(urls)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/football.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
