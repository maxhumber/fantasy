import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import re
from week import week

con = sqlite3.connect('projections.db')
cur = con.cursor()

league = 4319624
URL = f'http://fantasy.nfl.com/league/{league}/depthcharts'

response = requests.get(URL)
soup = BeautifulSoup(response.text, 'lxml')
df = pd.read_html(str(soup.findAll('table')[0]))[0]
df.columns = list(df.iloc[0].values)
df = df.drop(df.index[0])
df = pd.melt(df, id_vars=['Team'], var_name = 'position', value_name='players')
df['players'] = (
    df['players']
    .apply(
        lambda s: re.findall('[A-Z]\.\s[A-Z][a-z]+', s)
        if '.' in s
        else re.findall('([A-Z][a-z]*)', s)
    )
)
df = df.set_index(['Team', 'position'])
df = (df['players'].apply(pd.Series)
    .stack()
    .reset_index(level=2, drop=True)
    .to_frame('players')
)
df = df.reset_index().sort_values('Team', ascending=False)
df.columns = ['team', 'position', 'player']
df['week'] = week
df['fetched_at'] = pd.Timestamp('now')

df.to_sql('rosters', con, if_exists='append', index=False)
