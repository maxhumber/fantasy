import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import sqlite3

def _scrape(league=4319624):
    url = f'http://fantasy.nfl.com/league/{league}/depthcharts'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.findAll('table')[0]))[0]
    df.columns = list(df.iloc[0].values)
    df = df.drop(df.index[0])
    return df

def _transform(df):
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
    df.columns = ['team', 'position', 'name']
    df['fetched_at'] = pd.Timestamp('now')
    return df

def load(league=4319624):
    raw = _scrape(league)
    clean = _transform(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = load(league=4319624)
    df.to_sql('rosters', con, if_exists='append')
