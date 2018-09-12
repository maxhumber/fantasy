import sqlite3
from itertools import product
import requests
from bs4 import BeautifulSoup
import pandas as pd

pd.options.mode.chained_assignment = None

from utils.scoring import score_offense, score_kicking, score_defense, score
from utils.expand import expand_grid
from utils.columns import (
    FBDB_O_COLUMNS,
    FBDB_K_COLUMNS,
    FBDB_D_COLUMNS,
    O_COLUMNS,
    K_COLUMNS,
    D_COLUMNS,
    ALL_COLUMNS
)

URL = 'https://www.footballdb.com/fantasy-football/index.html'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def _scrape(payload):
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
    return df

def _transform(df, payload):
    if payload['pos'] in ('QB', 'RB', 'WR', 'TE'):
        df.columns = FBDB_O_COLUMNS
        df['two_point_conversions'] = (
            df['passing_two_point_conversions'] +
            df['receiving_two_point_conversions']
        )
        df = df[O_COLUMNS]
    elif payload['pos'] == 'K':
        df.columns = FBDB_K_COLUMNS
        df = df[K_COLUMNS]
    elif payload['pos'] == 'DST':
        df.columns = FBDB_D_COLUMNS
        payload['pos'] = 'DEF'
        df = df[D_COLUMNS]
    else:
        return None
    df['position'] = payload['pos']
    if int(payload['yr']) == 2018:
        df['week'] = payload['wk']
    else:
        df['week'] = f"{payload['yr']}-{payload['wk']}"
    return df

def load(week):
    payloads = expand_grid({
        'rules': [1],
        'pos': ['QB', 'RB', 'WR', 'TE', 'K', 'DST'],
        'yr': [2018],
        'wk': [week]
    })
    payloads = payloads.to_dict(orient='records')
    df = pd.DataFrame()
    for payload in payloads:
        d = _scrape(payload)
        d = _transform(d, payload)
        df = df.append(d, sort=False)
    df = df[ALL_COLUMNS]
    df['points'] = df.apply(lambda row: score(row), axis=1)
    return df

load(1)
