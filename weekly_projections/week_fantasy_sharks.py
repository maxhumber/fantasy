import pandas as pd
import requests
import sqlite3
from bs4 import BeautifulSoup



URL = 'https://www.fantasysharks.com/apps/bert/forecasts/projections.php'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

today = pd.Timestamp('today')
# today = pd.Timestamp('2018-09-11')
start = pd.Timestamp('2018-09-03')
week = (today - start).days // 7 + 1
segment = 628 + week - 1

payloads = [
    {'scoring': 13, 'Segment': segment, 'Position': 97},
    {'scoring': 13, 'Segment': segment, 'Position': 7},
    {'scoring': 13, 'Segment': segment, 'Position': 6}
    ]

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
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week']]
    return df

df = pd.DataFrame()
for payload in payloads:
    d = etl(payload)
    df = df.append(d)


df['source'] = 'Fantasy Pros'
df['fetched_at'] = pd.Timestamp('now')
df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
df.to_sql(f'projections', con, if_exists='append', index=False)

df.to_csv('week_1_fantasy_sharks.csv', index=False)
