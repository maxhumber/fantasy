import sqlite3
from itertools import product

import requests
from bs4 import BeautifulSoup
import pandas as pd

from fantasy.utils.week import week
from fantasy.utils.scoring import score
from fantasy.utils.columns import (
    FBDB_O_COLUMNS, O_COLUMNS,
    FBDB_K_COLUMNS, K_COLUMNS,
    FBDB_D_COLUMNS, D_COLUMNS,
    ALL_COLUMNS
)

pd.options.mode.chained_assignment = None

URL = 'https://www.footballdb.com/fantasy-football/index.html'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def _scrape_one(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    [s.extract() for s in soup.find_all(class_='visible-xs-inline')]
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    df = df.T.reset_index().T
    if payload['pos'] in ('K', 'DST'):
        df.columns = list(df.iloc[0].values)
        df = df.drop(df.index[0])
    else:
        df.columns = list(df.iloc[1].values)
        df = df.drop(df.index[[0, 1]])
    df['position'] = payload['pos'] if payload['pos'] != 'DST' else 'DEF'
    df['week'] = payload['wk']
    df['season'] = payload['yr']
    return df

def _transform(df):
    position = df['position'].unique()[0]
    if position in ['QB', 'RB', 'WR', 'TE']:
        df.columns = FBDB_O_COLUMNS
        df['two_point_conversions'] = (
            df['passing_two_point_conversions'] +
            df['receiving_two_point_conversions'])
        df = df[O_COLUMNS]
    elif position == 'K':
        df.columns = FBDB_K_COLUMNS
        df = df[K_COLUMNS]
    elif position == 'DEF':
        df.columns = FBDB_D_COLUMNS
        df = df[D_COLUMNS]
    else:
        return None
    return df

def load(week, season=2018):
    combos = product([1], ['QB', 'RB', 'WR', 'TE', 'K', 'DST'], [week], [season])
    payloads = [{'rules': c[0], 'pos': c[1], 'wk': c[2], 'yr': c[3]} for c in combos]
    df = pd.DataFrame()
    for payload in payloads:
        raw = _scrape_one(payload)
        clean = _transform(raw)
        df = df.append(clean, sort=False)
    df = df[ALL_COLUMNS]
    df['points'] = df.apply(lambda row: score(row), axis=1)
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week=week-1, season=2018)
    df.to_sql('points', con, if_exists='append', index=False)
    con.commit()
    con.close()
