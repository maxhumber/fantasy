import sqlite3
import re
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup
import pandas as pd

from utils.fuzzy import fuzzy_lookup

URL = 'http://fantasy.nfl.com/draftcenter/breakdown'

def _create_payloads(season):
    PAYLOAD = {'sort': 'draftAveragePosition', 'position': 'all', 'season': season}
    payloads = []
    for i in range(1, 1000, 25):
        payload = {**PAYLOAD, **{'offset': i}}
        payloads.append(payload)
    return payloads

def _scrape_one(payload):
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    picks = soup.find_all('tr', {'class': re.compile('players.*')})
    df = pd.DataFrame([
        {
            'name': pick.td.a.get_text(),
            'pos_team': pick.td.em.get_text(),
            'adp': pick.find(class_='playerDraftAvgPick').get_text()
        } for pick in picks
    ])
    df['season'] = payload['season']
    return df

def _scrape(payloads):
    df = pd.DataFrame()
    for payload in payloads:
        d = _scrape_one(payload)
        df = df.append(d, sort='False')
    return df

def _transform(df):
    df[['position', 'team']] = df['pos_team'].str.split(' - ', n=1, expand=True)
    return df[['name', 'position', 'team', 'adp', 'season']]

def load(season):
    payloads = _create_payloads(season)
    raw = _scrape(payloads)
    clean = _transform(raw)
    return clean

def scrape_seasons(start, end):
    seasons = range(start, end + 1)
    df = pd.DataFrame()
    for season in seasons:
        d = load(season)
        df = df.append(d, sort=False)
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = scrape_seasons(2015, 2018)
    df_draft = pd.read_csv('draft/draft.csv')
    df_draft['name'] = df_draft.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)
    df = pd.merge(df, df_draft, how='left', on=['name', 'position', 'season'])
    df = df.rename(columns={'team_y': 'team'})
    df = df.drop('team_x', axis=1)
    df.to_sql('draft', con, if_exists='replace', index=False)
    con.commit()
    con.close()
