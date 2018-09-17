import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd

from utils.week import week
from utils.fuzzy import fuzzy_lookup, fuzzy_cleanup

URL = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'

SEGMENT_START = {
    2015: 532,
    2016: 564,
    2017: 596,
    2018: 628
}

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def _create_payload(week, season=2018):
    base = {'scoring': 13, 'Position': 99}
    if season == 2018 and week == 'all':
        return {**base, **{'Segment': 621}}
    else:
        return {**base, **{'Segment': SEGMENT_START[season] - 1 + week}}

def _scrape(payload):
    segment = payload['Segment']
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='separator'):
        s.extract()
    df = pd.read_html(str(soup.find('div', class_='toolDiv')))[0]
    df.columns = list(df.iloc[0].values)
    if segment == 621:
        df['week'] = 'all'
        df['season'] = 2018
    else:
        season = [k for k, v in SEGMENT_START.items() if v <= segment][-1]
        week = segment - SEGMENT_START[season] + 1
        df['week'] = week
        df['season'] = season
    return df

def _transform(df):
    df['Pts'] = pd.to_numeric(df['Pts'], errors='coerce')
    df = df.dropna(subset=['Pts'])
    df = df.rename(columns={'Player': 'name', 'Tm': 'team', 'Opp': 'opponent', 'Pts': 'points', 'Position': 'position'})
    if 'opponent' in df:
        df['opponent'] = df['opponent'].str.replace('@', '')
    else:
        df['opponent'] = None
    df['name'] = df['name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
    df.loc[df['position'] == 'D', 'position'] = 'DEF'
    df['fuzzy_name'] = df.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)
    df = fuzzy_cleanup(df)
    df = df[df['position'].isin(['QB', 'WR', 'RB', 'TE', 'K', 'DEF'])]
    df['source'] = 'Fantasy Sharks'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'season', 'source', 'fetched_at']]
    return df

def load(week, season=2018):
    payload = _create_payload(week, season)
    raw = _scrape(payload)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
