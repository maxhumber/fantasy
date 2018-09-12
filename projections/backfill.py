import pandas as pd
import requests
import sqlite3
from bs4 import BeautifulSoup
from itertools import product

from projections.fantasy_sharks import load, URL, headers

def _create_weeks():
    years = [2015, 2016, 2017]
    weeks = list(range(1, 17 + 1))
    combos = list(product(years, weeks))
    return [f'{c[0]}-{c[1]}' for c in combos]

def _scrub_bad_data(df):
    df['team'] = None
    df['opponent'] = None
    return df

def backfill():
    weeks = _create_weeks()
    raw = pd.DataFrame()
    for week in weeks:
        d = load(week)
        raw = raw.append(d)
    clean = _scrub_bad_data(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = backfill()
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
