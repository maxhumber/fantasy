import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://www.fantasypros.com/nhl/rankings/overall.php'

def load():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.find_all('table')[0]))[0]
    df.columns = ['rank', 'name', 'position', 'team', 'best', 'worst', 'average', 'std']
    df['season'] = '2018-19'
    df['source'] = 'Fantasy Pros'
    df['fetched_at'] = pd.Timestamp('now')
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    df = load()
    df.to_sql('ranks', con, if_exists='replace', index=False)
    con.commit()
    con.close()
