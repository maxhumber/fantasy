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

def _create_payload(week):
    '''
    Acceptable: 'all', 1 - 17, '2015-x', '2016-x', '2017-x'
    '''
    base = {'scoring': 13, 'Position': 99}
    if week == 'all':
        return {**base, **{'Segment': 621}}
    elif type(week) == int:
        return {**base, **{'Segment': 628 + week - 1}}
    elif week[:4] == '2015':
        return {**base, **{'Segment': 531 + int(week.split('-')[1])}}
    elif week[:4] == '2016':
        return {**base, **{'Segment': 563 + int(week.split('-')[1])}}
    elif week[:4] == '2017':
        return {**base, **{'Segment': 595 + int(week.split('-')[1])}}
    else:
        return None

def _scrape(payload):
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
    payload = _create_payload(week)
    raw = _scrape(payload)
    clean = _transform(raw, week)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
