import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://www.fantasypros.com/nhl/adp/overall.php'

def load():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.find_all('table')[0]))[0]
    df[['first', 'last', 'team']] = df['Player Team'].str.split(' ', n=2, expand=True)
    df['name'] = df['first'] + ' ' + df['last']
    # fix JVR
    df.loc[df['name'] == 'James Van', 'team'] = 'PHI'
    df.loc[df['name'] == 'James Van', 'name'] = 'James Van Riemsdyk'
    df.columns = [c.lower() for c in df.columns]
    df = df[['name', 'team', 'yahoo', 'espn', 'cbs', 'avg']]
    df[['yahoo', 'espn', 'cbs', 'avg']] = df[['yahoo', 'espn', 'cbs', 'avg']].apply(pd.to_numeric)
    df['season'] = '2018-19'
    df['source'] = 'Fantasy Pros'
    df['fetched_at'] = pd.Timestamp('now')
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    df = load()
    df.to_sql('orders', con, if_exists='replace', index=False)
    con.commit()
    con.close()
