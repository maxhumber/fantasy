import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

def scrape_position(position):
    url = f'https://www.cbssports.com/fantasy/hockey/stats/{position}/2019/season/projections/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    table = soup.find('table', {'class': 'TableBase-table'})
    pdf = pd.read_html(str(table))[0]
    return pdf

df = pd.DataFrame()
for position in tqdm(['C', 'W', 'D', 'G']):
    pdf = scrape_position(position)
    df = df.append(pdf)
    time.sleep(1)

column_mappings = {
    'Player': 'name',
    'g  Goals': 'goals',
    'a  Assists': 'assists',
    'sog  Shots on Goal': 'shots_on_goal',
    '+/-  Plus-Minus Goals Scored For Or Against Total': 'plus_minus',
    'ppg  Powerplay Goals': 'powerplay_points',
    'sv  Saves': 'saves',
    'gaa  Goals Against Average': 'goals_against_average',
    'so  Shutouts': 'shutouts',
    'w  Wins': 'wins'
}

df = df.reset_index(drop=True)
df = df.rename(columns=column_mappings)
df = df[list(column_mappings.values())]



df.info()

def _transform(df):
    df = df.apply(pd.to_numeric, errors='ignore')
    df = df.reset_index(drop=True)

    df[['name', 'team']] = df['name'].str.split(',\s', n=1, expand=True)
    df['powerplay_points'] = None
    df['games'] = None
    df['hits'] = None
    df['blocks'] = None
    df['shots_on_goal'] = None
    df['season'] = '2018-19'
    columns = ['season', 'name', 'team', 'position', 'games']
    columns.extend(CATEGORIES)
    df = df[columns]
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df['source'] = 'CBS'
    df['fetched_at'] = pd.Timestamp('now')
    return df


if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    df = load()
    df.to_sql('projections', con, if_exists='replace', index=False)
    con.commit()
    con.close()
