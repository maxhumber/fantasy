import re
import sqlite3
from itertools import product

import requests
from bs4 import BeautifulSoup
import pandas as pd

from utils.fuzzy import fuzzy_lookup

def _create_payloads(teams=14, league=4319624):
    return [{'team': team, 'league': league} for team in range(1, teams + 1)]
    combos = list(product(range(1, teams + 1), [league]))

def _scrape_one(payload):
    url = f"http://fantasy.nfl.com/league/{payload['league']}/team/{payload['team']}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    team = soup.find('span', class_='label').get_text()
    players = soup.find_all('td', class_='playerNameAndInfo')
    df = pd.DataFrame([
        {'name': player.a.get_text(), 'pos_team': player.em.get_text()}
        for player in players
    ])
    df['position'] = df['pos_team'].str.split(' - ', n=1, expand=True)[0]
    df['team'] = team
    return df

def _scrape(payloads):
    df = pd.DataFrame()
    for payload in payloads:
        d = _scrape_one(payload)
        df = df.append(d)
    return df

def _transform(df):
    df = df.reset_index().sort_values(['team', 'position'], ascending=False)
    df = df[['team', 'position', 'name']]
    df['name'] = df.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)
    df['fetched_at'] = pd.Timestamp('now')
    return df

def load(teams=14, league=4319624):
    payloads = _create_payloads(teams, league)
    raw = _scrape(payloads)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db', isolation_level=None)
    cur = con.cursor()
    con.commit()
    df = load(teams=14, league=4319624)
    df.to_sql('rosters', con, if_exists='append', index=False)
    con.commit()
    con.close()
