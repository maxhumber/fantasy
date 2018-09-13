import pandas as pd
import sqlite3
pd.options.display.max_rows = 999

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

df = pd.read_csv('data/projections.csv')
df[['season2', 'week2']] = df['week'].str.split('-', expand=True)

df['season2'].unique()

df.loc[df['season2'] == '1', 'week2'] = '1'
df.loc[df['season2'] == '2', 'week2'] = '2'
df.loc[df['season2'] == 'all', 'week2'] = 'all'

df.loc[df['season2'] == '1', 'season2'] = 2018
df.loc[df['season2'] == '2', 'season2'] = 2018
df.loc[df['season2'] == 'all', 'season2'] = 2018

df = df.drop('week', axis=1)
df = df.drop('season', axis=1)

df = df.rename(columns={'week2': 'week', 'season2': 'season'})
df = df[['name', 'position', 'team', 'opponent', 'points', 'week', 'season', 'source', 'fetched_at']]
df['season'].unique()
df['season'] = pd.to_numeric(df['season'])

df = df.sort_values(['season', 'week', 'source', 'name'])

cur.execute('delete from projections')
con.commit()
cur.execute('vacuum')

df.to_sql('projections', con, if_exists='append', index=False)
con.commit()
con.close()
