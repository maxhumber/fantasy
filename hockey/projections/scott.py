import sqlite3
import pandas as pd

from hockey.utils import CATEGORIES

df = pd.read_csv('data/2018-2019_scott_cullen.csv')
df.columns = [c.lower() for c in df.columns]
df = df.rename(columns={
    'player': 'name',
    'pos': 'position',
    'gp': 'games',
    'g': 'goals',
    'a': 'assists',
    'plusminus': 'plus_minus',
    'ppp': 'powerplay_points',
    'sog': 'shots_on_goal',
    'w': 'wins',
    'avg': 'goals_against_average',
    'sv%': 'save_percentage',
    'so': 'shutouts'})
df['season'] = '2018-19'
df['saves'] = None
df['source'] = 'Scott Cullen'
df['fetched_at'] = pd.Timestamp('now')
df = df[['season', 'name', 'team', 'position', 'games', 'goals', 'assists',
       'plus_minus', 'powerplay_points', 'shots_on_goal', 'hits', 'blocks',
       'wins', 'goals_against_average', 'saves', 'save_percentage', 'shutouts',
       'source', 'fetched_at']]

if __name__ == '__main__':
    con = sqlite3.connect('data/hockey.db')
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
