import pandas as pd
import numpy as np
import requests
import time
import sqlite3
from bs4 import BeautifulSoup

# configuration

con = sqlite3.connect('nfl.db')
cur = con.cursor()
URL = 'http://games.espn.com/ffl/tools/projections'

# fetch one table

def fetch_table(slot, offset=0):
    payload = {'slotCategoryId': slot, 'startIndex': offset}
    response = requests.get(URL, params=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.findAll('table')[1]))[0]
    df.columns = list(df.iloc[1].values)
    df = df.drop(df.index[[0, 1]])
    df = df[['PLAYER, TEAM POS', 'PTS']]
    return df

# fetch all the tables

def fetch_all(combos):
    all = pd.DataFrame()
    for index, row in combos.iterrows():
        try:
            df = fetch_table(row['slot'], row['offset'])
            all = pd.concat([all, df])
        except IndexError:
            print(f'Could not fetch ({row["slot"]}, {row["offset"]})')
        finally:
            time.sleep(0.1)
    print('Finished')
    return all

# clean and parse the stats table

def clean_table(df):
    df = df.reset_index(drop=True)
    df[['name', 'pos_team']] = df['PLAYER, TEAM POS'].str.split(', ', expand=True)
    df[['team', 'pos']] = df['pos_team'].str.split('\\s', expand=True).iloc[:, [0, 1]]
    df = df.rename(columns={'PTS': 'points'})
    df = df[['name', 'pos', 'team', 'points']]
    df['name'] = df['name'].str.replace('*', '')
    df['name'] = df['name'].str.replace('\\sD/ST\\sD/ST', '')
    df.fillna(value=np.nan, inplace=True)
    df['pos'].fillna('DEF', inplace=True)
    team_codes = (
        pd.read_sql('select * from teams', con)
        .set_index('team')
        .to_dict(orient='dict')
        ['code']
    )
    df.loc[df['pos'] == 'DEF', ['team']] = df[df['pos'] == 'DEF']['name'].map(team_codes)
    df['points'] = df['points'].apply(pd.to_numeric)
    df = df.sort_values('points', ascending=False)
    return df

# actual hydration

if __name__ == '__main__':
    combos = pd.read_sql('select * from combos', con)
    df = fetch_all(combos)
    df = clean_table(df)
    df.to_sql('stats', con, if_exists='replace', index=False)
