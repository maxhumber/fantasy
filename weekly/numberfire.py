import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

URL = 'http://www.numberfire.com/nfl/fantasy/fantasy-football-projections'

def _scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.findAll('span', {'class': 'abbrev'}):
        s.extract()
    names = pd.read_html(str(soup.findAll('table')[0]))[0]
    data = pd.read_html(str(soup.findAll('table')[1]))[0]
    df = pd.concat([names, data], axis=1)
    if url[-1] in ('k', 'd'):
        df = df.iloc[:, 0:4]
        df.columns = ['name', 'points', 'ci', 'opponent']
        df = df.drop('ci', axis=1)
    else:
        df = df.iloc[:, 0:3]
        df.columns = ['name', 'points', 'opponent']
    week = str(soup.find(class_='projection-rankings__hed').find('h2'))
    week = int(re.findall('Week\s(.*?)\sFantasy', week)[0])
    df['week'] = week
    return df

def _transform():
    urls = [URL, URL + '/k', URL + '/d']
    df = pd.DataFrame()
    for url in urls:
        d = _scrape(url)
        df = df.append(d)
    df = df.reset_index(drop=True)
    df[['name', 'position']] = df['name'].str.split('\s\s\(', n=1, expand=True)
    df[['position', 'team']] = df['position'].str.split(', ', n=1, expand=True)
    df['team'] = df['team'].str.replace(')', '')
    df['name'] = df['name'].str.replace('\sD/ST', '')
    df.loc[df['position'] == 'D', 'position'] = 'DEF'
    df['source'] = 'numberFire'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    return df

def load():
    clean = _transform()
    return clean
