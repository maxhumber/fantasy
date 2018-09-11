# Fantasy Sharks
# https://www.fantasysharks.com/apps/Projections/SeasonProjections.php?pos=ALL&format=json&l=13

import requests
import pandas as pd
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# fetch

URL = 'https://www.fantasysharks.com/apps/Projections/SeasonProjections.php'
payload = {'pos': 'ALL', 'format': 'json', 'l': 13}
headers = {
    'User-Agent': 'request',
    'Accept': 'application/json'
}

response = requests.get(URL, params=payload, headers=headers)
data = response.json()
df = pd.DataFrame(data)

# clean

df = df[['Name', 'Team', 'Pos', 'FantasyPoints']]
df['Name'] = df['Name'].str.replace(r'(.+),\s+(.+)', r'\2 \1')
df.columns = ['name', 'team', 'position', 'points']
df = df[['name', 'position', 'team', 'points']]

# dump

df.to_sql('draft_fantasy_sharks', con, if_exists='replace', index=False)
