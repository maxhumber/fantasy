# NFL
# http://fantasy.nfl.com/draftcenter/breakdown?leagueId=4319624#draftCenterBreakdown=draftCenterBreakdown%2C%2Fdraftcenter%2Fbreakdown%253FleagueId%253D4319624%2526offset%253D26%2526position%253Dall%2526season%253D2018%2526sort%253DdraftAveragePosition%2Creplace

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# malformed URL

# from urllib.parse import urlparse, unquote
# url = 'http://fantasy.nfl.com/draftcenter/breakdown?leagueId=4319624#draftCenterBreakdown=draftCenterBreakdown%2C%2Fdraftcenter%2Fbreakdown%253FleagueId%253D4319624%2526offset%253D26%2526position%253Dall%2526season%253D2018%2526sort%253DdraftAveragePosition%2Creplace'
# url = unquote(unquote(url))
# urlparse(url)

# fetch

URL = 'http://fantasy.nfl.com/draftcenter/breakdown'
p = {
    'leagueId': '4319624',
    'position': 'all',
    'season': '2018',
    'sort': 'draftAveragePosition'
}

df = pd.DataFrame()
for i in range(1, 400, 25):
    payload = {**p, **{'offset': i}}
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    for s in soup.find_all(class_='playerNote'):
        s.extract()
    for s in soup.find_all('em'):
        s.extract()
    d = pd.read_html(str(soup.findAll('table')[0]))[0]
    df = df.append(d)

# clean
df = df.reset_index(drop=True)
df = df[['Player', 'Avg. Pick (ADP)']]
df.columns = ['name', 'nfl_adp']

# dump

df.to_sql('adp_nfl', con, if_exists='replace', index=False)
