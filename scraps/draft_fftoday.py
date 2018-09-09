# FFToday
# http://www.fftoday.com/rankings/playerproj.php?Season=2018&PosID=10&LeagueID=143908

import requests
import pandas as pd
from bs4 import BeautifulSoup

mappings = {'qb': 10, 'rb': 20, 'wr': 30, 'te': 40, 'k': 80, 'def': 99}
for k, v in mappings.items():
    print(k, v)

URL = 'http://www.fftoday.com/rankings/playerproj.php'
payload = {
    'Season': 2018,
    'LeagueID': 143908,
    'sort_order': 'DESC',
    'PosID': 20,
    'cur_page': 0}
response = requests.get(URL, payload)
soup = BeautifulSoup(response.text, 'lxml')

# 11
d = pd.read_html(str(soup.findAll('table')[3]))[0]
d.columns = list(d.iloc[11].values)
d = d.drop(d.index[0:12])
d[['Player Sort First: Last:', 'Team', 'FPts']]





df = pd.DataFrame()
positions = ['qb', 'rb', 'wr', 'te', 'k', 'dst']
for p in positions:
    print(p)
    url = f'https://www.fantasypros.com/nfl/projections/{p}.php?week=draft'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    d = pd.read_html(str(soup.findAll('table')[0]))[0]
    d = d.T.reset_index().T
    if p in ('qb', 'rb', 'wr', 'te'):
        d.columns = list(d.iloc[1].values)
        d = d.drop(d.index[[0, 1]])
    else:
        d.columns = list(d.iloc[0].values)
        d = d.drop(d.index[0])
    d = d[['Player', 'FPTS']]
    df = df.append(d)

df = df.reset_index(drop=True)
