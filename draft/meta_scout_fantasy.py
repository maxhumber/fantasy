# Scout Fantasy
# https://fftoolbox.scoutfantasysports.com/football/rankings/index.php?noppr=true

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# fetch

URL = 'https://fftoolbox.scoutfantasysports.com/football/rankings/index.php?noppr=true'

response = requests.get(URL, verify=False)
soup = BeautifulSoup(response.text, 'lxml')
for s in soup.findAll('span', {'class': 'player-detail-icons'}):
    s.extract()
df = pd.read_html(str(soup.findAll('table')[0]))[0]

# clean
df = df[['Player', 'Bye', 'Injury', 'Age', 'ADP']]
df.columns = ['name', 'bye', 'injury', 'age', 'adp']
df = df.dropna(axis='rows', how='all')
df = df.sort_values('adp')
df = df[df['adp'] != 0]

# dump

df.to_sql('meta_scout_fantasy', con, if_exists='replace', index=False)
