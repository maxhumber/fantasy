import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd

from utils.week import week
from utils.fuzzy import fuzzy_lookup

URL = 'http://games.espn.com/ffl/tools/projections'

def _create_payloads(week, season):
    payloads = []
    for i in range(0, 400, 40):
        if week == 'all':
            payload = {'seasonId': season, 'startIndex': i, 'seasonTotals': 'true'}
        else:
            payload = {'seasonId': season, 'startIndex': i, 'scoringPeriodId': week}
        payloads.append(payload)
    return payloads

def _scrape_one(payload):
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    df.columns = list(df.iloc[2].values)
    df = df.drop(df.index[0:3])
    if 'OPP' not in df:
        df['OPP'] = None
        # handle remaining year stats problem
        df['PTS'] = pd.to_numeric(df['PTS'], errors='coerce')
        df['PTS'] = round(df['PTS'] * (1 - ((week - 1) / 16)))
    df = df[['PLAYER, TEAM POS', 'PTS', 'OPP']]
    df['season'] = payload.get('seasonId')
    df['week'] = payload.get('scoringPeriodId', 'all')
    return df

def _scrape(payloads):
    df = pd.DataFrame()
    for payload in payloads:
        d = _scrape_one(payload)
        df = df.append(d)
    return df

def _transform(df):
    df = df.reset_index(drop=True)
    df[['name', 'pos_team']] = df['PLAYER, TEAM POS'].str.split(', ', expand=True).iloc[:, [0, 1]]
    df[['team', 'position']] = df['pos_team'].str.split('\\s', expand=True).iloc[:, [0, 1]]
    df = df.rename(columns={'PTS': 'points', 'OPP': 'opponent'})
    df['name'] = df['name'].str.replace('*', '').str.replace('\\sD/ST\\sD/ST', '')
    df.loc[df['position'].isnull(), 'position'] = 'DEF'
    df['name'] = df.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)
    df['opponent'] = df['opponent'].str.replace('@', '').str.upper()
    df['team'] = df['team'].str.upper()
    df['source'] = 'ESPN'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'season', 'source', 'fetched_at']]
    return df

def load(week, season=2018):
    payloads = _create_payloads(week, season)
    raw = _scrape(payloads)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
