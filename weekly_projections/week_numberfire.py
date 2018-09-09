# Numberfire
# http://www.numberfire.com/nfl/fantasy/remaining-projections

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import re

today = pd.Timestamp('today')
# today = pd.Timestamp('2018-09-11

start = pd.Timestamp('2018-09-03')
week = (today - start).days // 7 + 1

# fetch

URL = 'http://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
urls = [URL, URL + '/k', URL + '/d']

def scrape(url):
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
    nf_week = str(soup.find(class_='projection-rankings__hed').find('h2'))
    nf_week = int(re.findall('Week\s(.*?)\sFantasy', nf_week)[0])
    df['week'] = nf_week
    return df

df = pd.DataFrame()
for url in urls:
    d = scrape(url)
    df = df.append(d)

# clean

df[['name', 'position']] = df['name'].str.split('\s\s\(', n=1, expand=True)
df[['position', 'team']] = df['position'].str.split(', ', n=1, expand=True)
df['team'] = df['team'].str.replace(')', '')
df['name'] = df['name'].str.replace('\sD/ST', '')
df.loc[df['position'] == 'D', 'position'] = 'DEF'
df = df[['name', 'position', 'team', 'opponent', 'points', 'week']]

df.to_csv('week_1_numberfire.csv', index=False)
