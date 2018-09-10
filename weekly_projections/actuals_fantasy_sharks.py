import pandas as pd
import requests
import sqlite3
from bs4 import BeautifulSoup
from week import week
from fuzzy_defence import fuzzy_defence

con = sqlite3.connect('projections.db')
cur = con.cursor()

URL = 'https://www.fantasysharks.com/apps/bert/stats/points.php'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

payload = {'scoring': 13, 'Segment': 628 + week - 1, 'Position': 99}

def scrape(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.find('div', class_='toolDiv')))[0]
    return df

def etl(payload):
    df = scrape(payload)
    df.columns = list(df.iloc[0].values)
    df['Pts'] = pd.to_numeric(df['Pts'], errors='coerce')
    df = df.dropna(subset=['Pts'])
    df = df.rename(columns={'Player': 'name', 'Team': 'team', 'Opp': 'opponent', 'Pts': 'points', 'Position': 'position'})
    df['opponent'] = df['opponent'].str.replace('@', '')
    df['name'] = df['name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
    df.loc[df['position'] == 'D', 'position'] = 'DEF'
    df['week'] = week
    df['source'] = 'Fantasy Sharks'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    df.to_sql('actuals', con, if_exists='append', index=False)

if __name__ == '__main__':
    etl(payload)
    print('Success!')
