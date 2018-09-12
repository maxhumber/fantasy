import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urlparse, unquote
from itertools import product

def fix_garbled_url():
    url = 'http://fantasy.nfl.com/draftcenter/breakdown?leagueId=4319624#draftCenterBreakdown=draftCenterBreakdown%2C%2Fdraftcenter%2Fbreakdown%253FleagueId%253D4319624%2526offset%253D26%2526position%253Dall%2526season%253D2018%2526sort%253DdraftAveragePosition%2Creplace'
    url = unquote(unquote(url))
    return url

URL = 'http://fantasy.nfl.com/draftcenter/breakdown'

def _create_payload(position='all', season='2018', offset=0):
    payload = {'sort': 'draftAveragePosition', 'position': position, 'season': season, 'offset': offset}
    return payload

def _scrape_one(payload):
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    [s.extract() for s in soup.find_all(class_='playerNote')]
    [s.extract() for s in soup.find_all(class_='status')]
    [s.extract() for s in soup.find_all('em')]
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    return df

def _scrape(season):
    df = pd.DataFrame()
    for i in range(1, 400, 25):
        payload = _create_payload(season=2018, offset=i)
        d = _scrape_one(payload)
        df = df.append(d)
    return df

def _transform(df, season):
    df = df.reset_index(drop=True)
    df = df[['Player', 'Avg. Pick (ADP)']]
    df.columns = ['name', 'adp']
    df['season'] = season
    return df

def load(season=2018):
    raw = _scrape(season)
    clean = _transform(raw, season)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    draft = pd.read_csv('draft/draft.csv')
    adp = load(season=2018)
    df = pd.merge(draft, adp, how='left', on='name')
    df.to_sql('draft', con, if_exists='replace', index=False)
    con.commit()
    con.close()
