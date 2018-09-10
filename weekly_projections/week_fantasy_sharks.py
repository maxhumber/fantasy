import pandas as pd
import requests
import sqlite3
from bs4 import BeautifulSoup
from week import week

con = sqlite3.connect('projections.db')
cur = con.cursor()

URL = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def create_payloads():
    segment = 628 + week - 1
    payloads = [
        {'scoring': 13, 'Segment': segment, 'Position': 97},
        {'scoring': 13, 'Segment': segment, 'Position': 7},
        {'scoring': 13, 'Segment': segment, 'Position': 6}
        ]
    return payloads

def scrape(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='separator'):
        s.extract()
    df = pd.read_html(str(soup.find('div', class_='toolDiv')))[0]
    return df

def etl(payload):
    df = scrape(payload)
    df.columns = list(df.iloc[0].values)
    df['Pts'] = pd.to_numeric(df['Pts'], errors='coerce')
    df = df.dropna(subset=['Pts'])
    if payload['Position'] == 7:
        df['Position'] = 'K'
    if payload['Position'] == 6:
        df['Position'] = 'DEF'
    df = df.rename(columns={'Player': 'name', 'Tm': 'team', 'Opp': 'opponent', 'Pts': 'points', 'Position': 'position'})
    df['opponent'] = df['opponent'].str.replace('@', '')
    df['name'] = df['name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
    df['week'] = week
    df['source'] = 'Fantasy Sharks'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    df.to_sql('projections', con, if_exists='append', index=False)

if __name__ == '__main__':
    payloads = create_payloads()
    for payload in payloads:
        etl(payload)
    print('Success!')
