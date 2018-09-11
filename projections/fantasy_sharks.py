import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from utils.week import week

URL = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def _create_payload():

def _scrape(week):
    if week == 'all':
        payload = {'scoring': 13, 'Segment': 621, 'Position': 99}
    else:
        payload = {'scoring': 13, 'Segment': 628 + week - 1, 'Position': 99}
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='separator'):
        s.extract()
    df = pd.read_html(str(soup.find('div', class_='toolDiv')))[0]
    return df

def _transform(df, week):
    df.columns = list(df.iloc[0].values)
    df['Pts'] = pd.to_numeric(df['Pts'], errors='coerce')
    df = df.dropna(subset=['Pts'])
    df = df.rename(columns={'Player': 'name', 'Tm': 'team', 'Opp': 'opponent', 'Pts': 'points', 'Position': 'position'})
    if 'opponent' in df:
        df['opponent'] = df['opponent'].str.replace('@', '')
    else:
        df['opponent'] = None
    df['name'] = df['name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
    df.loc[df['position'] == 'D', 'position'] = 'DEF'
    df['week'] = week
    df['source'] = 'Fantasy Sharks'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    return df

def load(week):
    raw = _scrape(week)
    clean = _transform(raw, week)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
