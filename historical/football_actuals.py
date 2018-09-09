# Football DB
# https://www.footballdb.com/fantasy-football/index.html?pos=QB&yr=2017&wk=1&rules=1

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
from itertools import product

con = sqlite3.connect('football.db')
cur = con.cursor()

URL = 'https://www.footballdb.com/fantasy-football/index.html'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def expand_grid(dictionary):
    return pd.DataFrame(
        [row for row in product(*dictionary.values())],
        columns=dictionary.keys()
    )

def create_payloads():
    payloads = {
        'rules': [1],
        'pos': ['QB', 'RB', 'WR', 'TE', 'K', 'DST'],
        'yr': list(range(2010, 2017 + 1)),
        'wk': list(range(1, 17 + 1))
    }
    payloads = expand_grid(payloads)
    payloads = payloads.to_dict(orient='records')
    return payloads

def scrape(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='visible-xs-inline'):
        s.extract()
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    df = df.T.reset_index().T
    if payload['pos'] in ('K', 'DST'):
        df.columns = list(df.iloc[0].values)
        df = df.drop(df.index[0])
    else:
        df.columns = list(df.iloc[1].values)
        df = df.drop(df.index[[0, 1]])
    return df

O_COLUMNS = [
    'name', 'game', 'points',
    'passing_attempts', 'passing_completions', 'passing_yards',
    'passing_touchdowns', 'passing_interceptions', 'passing_two_point_conversions',
    'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 'rushing_two_point_conversions',
    'receiving_receptions', 'receiving_yards', 'receiving_touchdowns', 'receiving_two_point_conversions',
    'fumbles_lost', 'fumbles_touchdowns'
]

K_COLUMNS = [
    'name', 'game', 'points',
    'extra_points_attempted', 'extra_points_made',
    'field_goals_attempted', 'field_goals_made', 'over_50_yard_field_goals_made'
]

D_COLUMNS = [
    'name', 'opponent', 'points',
    'sacks', 'interceptions', 'safeties', 'fumble_recoveries', 'blocked_kicks',
    'touchdowns', 'points_allowed', 'passing_yards_allowed',
    'rushing_yards_allowed', 'total_yards_allowed'
]

def etl(payload):
    df = scrape(payload)
    if payload['pos'] in ('QB', 'RB', 'WR', 'TE'):
        df.columns = O_COLUMNS
    elif payload['pos'] == 'K':
        df.columns = K_COLUMNS
    else:
        df.columns = D_COLUMNS
        payload['pos'] = 'DEF'
    df['year'] = payload['yr']
    df['week'] = payload['wk']
    df.to_sql(f'actuals_{payload["pos"].lower()}', con, if_exists='append', index=False)
    return None

if __name__ == '__main__':
    payloads = create_payloads()
    for payload in payloads:
        try:
            etl(payload)
            print(f'Success: {payload}')
        except:  # YOLO
            print(f'Failed: {payload}')
    print('Finished!')
