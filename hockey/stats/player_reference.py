import re
import sqlite3
import string

import requests
from bs4 import BeautifulSoup
import pandas as pd

def _create_payloads(teams, league):
    return [{'team': team, 'league': league} for team in range(1, teams + 1)]
    combos = list(product(range(1, teams + 1), [league]))

url = 'https://www.hockey-reference.com/players/a/abdelju01.html'
url = 'https://www.hockey-reference.com/players/g/gibsojo02.html'

def _scrape_player(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    name = soup.find('h1', attrs={'itemprop': 'name'}).get_text()
    position = soup.find('p').get_text()
    try:
        position = re.findall('\:(.*?)\xa0', position)[0].strip()
    except IndexError:
        position = re.findall('\:(.*?)\n', position)[0].strip()
    soup = soup.find('table', attrs={'id': 'stats_basic_plus_nhl'})
    soup = soup.find_all('tr', attrs={'id': re.compile('stats_basic_plus_nhl')})
    seasons = []
    for s in soup:
        season = {'season': s.find('th').get_text()}
        for e in s.find_all('td'):
            season = {**season, **{e.get('data-stat'): e.get_text('data-stat')}}
        seasons.append(season)
    df = pd.DataFrame(seasons)
    df['name'] = name
    df['position'] = position
    return df

df = _scrape_player('https://www.hockey-reference.com/players/g/gibsojo02.html')


#


url = 'https://www.hockey-reference.com/players/a/skaters.html'
response = requests.get(url)
soup = BeautifulSoup(response.text)


bowl = soup
soup = bowl

def extract_td(e, attr):
    return e.find('td', attrs={'data-stat': attr}).get_text()


for letter in string.ascii_lowercase:


def _scrape_letter(letter):
    url = f'https://www.hockey-reference.com/players/{letter}/skaters.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    players = []
    for p in soup.find('tbody').find_all('tr'):
        player = {
            'name': p.a.get_text(),
            'href': p.a.attrs['href'],
            'year_min': int(extract_td(p, 'year_min')),
            'year_max': int(extract_td(p, 'year_max')),
            'games_played': int(extract_td(p, 'games_played')),
            'position': extract_td(p, 'pos')
        }
        players.append(player)
    return [player['href'] for player in players if player['year_max'] >= 2017]
df



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

def load(teams, league):
    payloads = _create_payloads(teams, league)
    raw = _scrape(payloads)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/football.db')
    df = load(teams=14, league=4319624)
    df.to_sql('rosters', con, if_exists='append', index=False)
    con.commit()
    con.close()
