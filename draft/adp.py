import sqlite3
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fix_garbled_url():
    url = ('http://fantasy.nfl.com/draftcenter/breakdown?'
        'leagueId=4319624#draftCenterBreakdown=draftCenterBreakdown%2C%2F'
        'draftcenter%2Fbreakdown%253FleagueId%253D4319624%2526offset'
        '%253D26%2526position%253Dall%2526season%253D2018%2526sort'
        '%253DdraftAveragePosition%2Creplace')
    url = unquote(unquote(url))
    return url

URL = 'http://fantasy.nfl.com/draftcenter/breakdown'

def _create_payload(season, position='all', offset=0):
    payload = {
        'sort': 'draftAveragePosition', 'position': position,
        'season': season, 'offset': offset
    }
    return payload

def _scrape_one(payload):
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    [s.extract() for s in soup.find_all(class_='playerNote')]
    [s.extract() for s in soup.find_all(class_='status')]
    [s.extract() for s in soup.find_all('em')]
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    df['season'] = payload['season']
    return df

def load(season, position='all'):
    df = pd.DataFrame()
    for i in range(1, 400, 25):
        payload = _create_payload(season, position, offset=i)
        d = _scrape_one(payload)
        df = df.append(d)
    df = df.reset_index(drop=True)
    df = df.rename(columns={'Player': 'name', 'Avg. Pick (ADP)': 'adp'})
    df = df[['name', 'adp', 'season']]
    return df
