import requests
import pandas as pd
from bs4 import BeautifulSoup
from week import week
import sqlite3

con = sqlite3.connect('projections.db')
cur = con.cursor()

URL = 'http://games.espn.com/ffl/tools/projections'

def create_payloads():
    payloads = []
    for i in range(0, 400, 40):
        payload = {'seasonId': 2018, 'startIndex': i, 'scoringPeriodId': week}
        payloads.append(payload)
    return payloads

def scrape(payloads):
    df = pd.DataFrame()
    for payload in payloads:
        response = requests.get(URL, params=payload)
        soup = BeautifulSoup(response.text, 'lxml')
        d = pd.read_html(str(soup.findAll('table')[0]))[0]
        d.columns = list(d.iloc[2].values)
        d = d.drop(d.index[0:3])
        d = d[['PLAYER, TEAM POS', 'PTS', 'OPP']]
        df = df.append(d)
    return df

def etl(payloads):
    df = scrape(payloads)
    df = df.reset_index(drop=True)
    df[['name', 'pos_team']] = df['PLAYER, TEAM POS'].str.split(', ', expand=True).iloc[:, [0, 1]]
    df[['team', 'position']] = df['pos_team'].str.split('\\s', expand=True).iloc[:, [0, 1]]
    df = df.rename(columns={'PTS': 'points', 'OPP': 'opponent'})
    df.loc[df['position'].isnull(), 'position'] = 'DEF'
    df['name'] = df['name'].str.replace('*', '')
    df['name'] = df['name'].str.replace('\\sD/ST\\sD/ST', '')
    df['opponent'] = df['opponent'].str.replace('@', '')
    df['opponent'] = df['opponent'].str.upper()
    df['team'] = df['team'].str.upper()
    df['week'] = week
    df['source'] = 'ESPN'
    df['fetched_at'] = pd.Timestamp('now')
    df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'source', 'fetched_at']]
    df.to_sql('projections', con, if_exists='append', index=False)

if __name__ == '__main__':
    payloads = create_payloads()
    etl(payloads)
    print('Success!')
