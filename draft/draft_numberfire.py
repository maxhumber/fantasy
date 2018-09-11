# Numberfire
# http://www.numberfire.com/nfl/fantasy/remaining-projections

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# fetch

URL = 'http://www.numberfire.com/nfl/fantasy/remaining-projections'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'lxml')
for s in soup.findAll('span', {'class': 'abbrev'}):
    s.extract()
names = pd.read_html(str(soup.findAll('table')[0]))[0]
data = pd.read_html(str(soup.findAll('table')[1]))[0]
df = pd.concat([names, data], axis=1)

# clean

df = df.iloc[:, 0:2]
df.columns = ['name', 'points']
df[['name', 'position']] = df['name'].str.split('\s\s\(', n=1, expand=True)
df[['position', 'team']] = df['position'].str.split(', ', n=1, expand=True)
df['team'] = df['team'].str.replace(')', '')
df = df[['name', 'position', 'team', 'points']]

# dump

df.to_sql('draft_numberfire', con, if_exists='replace', index=False)
