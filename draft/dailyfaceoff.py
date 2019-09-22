import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# scrape
url = 'https://www.dailyfaceoff.com/fantasy-hockey-projections/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
df = pd.DataFrame()
table = soup.find('table', {'id': 'igsv-1N8XNZpOIb8-6WcOPANqSHRyHBXlwZ6X_1vgGyDbETm4'})
df = df.append(pd.read_html(str(table))[0])
table = soup.find('table', {'id': 'igsv-1-1N8XNZpOIb8-6WcOPANqSHRyHBXlwZ6X_1vgGyDbETm4'})
df = df.append(pd.read_html(str(table))[0])

# clean
df = df.reset_index(drop=True)
column_mappings = {
    'RANK': 'rank',
    'Name': 'name',
    'TEAM': 'team',
    'POS': 'position',
    'Pos. Rank': 'goalie',
    'G': 'goals',
    'A': 'assists',
    'PPP': 'powerplay_points',
    'SOG': 'shots_on_goal',
    'HIT': 'hits',
    'BLK': 'blocks',
    'W': 'wins',
    'GAA': 'goals_against_average',
    'SV%': 'save_percentage',
}
df = df.rename(columns=column_mappings)
df[column_mappings.values()]
