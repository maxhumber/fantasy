import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

URL = 'https://www.footballdb.com/players/current.html'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

def _scrape_one(payload):
    response = requests.get(URL, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='td hidden-xs'):
        s.extract()
    soup = soup.find_all('div', class_='td')
    players = []
    for s in soup:
        try:
            player = s.find('a')['title'].replace(' Stats', '')
            players.append(player)
        except TypeError:
            pass
        except KeyError:
            pass
    df = pd.DataFrame({'name': players})
    df['position'] = payload['pos']
    return df

def fetch():
    payloads = [{'pos': 'WR'}, {'pos': 'RB'}, {'pos': 'TE'}, {'pos': 'QB'}, {'pos': 'K'}]
    players = pd.DataFrame()
    for payload in payloads:
        d = _scrape_one(payload)
        players = players.append(d)
    players['updated_at'] = pd.Timestamp('now')
    return players

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = fetch()
    df.to_sql('players', con, if_exists='replace', index=False)
    con.commit()
