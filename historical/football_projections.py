import pandas as pd
import numpy as np
import requests
import time
import sqlite3
from bs4 import BeautifulSoup
from itertools import product
import random

con = sqlite3.connect('football.db')
cur = con.cursor()

URL = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def generate_weeks(year, start):
    return {v: f'{year}-{i+1}' for i, v in enumerate(range(start, start+17))}

weeks = {
    **generate_weeks(2015, 532),
    **generate_weeks(2016, 564),
    **generate_weeks(2017, 596)
}

positions = {
    1: 'QB',
    2: 'RB',
    4: 'WR',
    5: 'TE',
    7: 'K',
    6: 'DEF'
}

def expand_grid(dictionary):
    return pd.DataFrame(
        [row for row in product(*dictionary.values())],
        columns=dictionary.keys()
    )

def create_payloads():
    payloads = {
        'League': [-1],
        'scoring': [13],
        'uid':[4],
        'Position': positions.keys(),
        'Segment': weeks.keys()
    }
    payloads = expand_grid(payloads)
    payloads = payloads.to_dict(orient='records')
    return payloads

class renamer:
    def __init__(self):
        self.d = dict()

    def __call__(self, x):
        if x not in self.d:
            self.d[x] = 0
            return x
        else:
            self.d[x] += 1
            return f'{x}_{self.d[x]}'

def scrape(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='separator'):
        s.extract()
    df = pd.read_html(str(soup.find('div', class_='toolDiv')))[0]
    return df

def etl(payload):
    position = positions[payload['Position']]
    df = scrape(payload)
    df.columns = list(df.iloc[0].values)
    df = df.drop(df.index[0])
    df = df.dropna(subset=['Player'])
    df = df[(df['#'] != '#') & (df['Player'] != '0')]
    df = df.rename(columns=renamer())
    df = df.rename(columns={'Player': 'name', 'Tm': 'team', 'Opp': 'opponent', 'Pts': 'points'})
    df['opponent'] = df['opponent'].str.replace('@', '')
    df['name'] = df['name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
    df['position'] = position
    df['year'] = weeks[payload['Segment']]
    df[['year', 'week']] = df['year'].str.split('-', n=1, expand=True)
    df = df[['name', 'position', 'points', 'year', 'week']]
    df.to_sql(f'projections_{position.lower()}', con, if_exists='append', index=False)

if __name__ == '__main__':
    payloads = create_payloads()
    # payloads = random.sample(payloads, 10)
    for payload in payloads:
        try:
            etl(payload)
            print(f'Success: {payload}')
        except:  # YOLO
            print(f'Failed: {payload}')
