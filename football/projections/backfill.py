import sqlite3
from itertools import product

import requests
from bs4 import BeautifulSoup
import pandas as pd

from football.projections.fantasy_sharks import load, URL, headers, SEGMENT_START

def _create_weeks():
    years = [2015, 2016, 2017]
    weeks = list(range(1, 17 + 1))
    combos = list(product(years, weeks))
    return combos

def _scrub_bad_data(df):
    df['team'] = None
    df['opponent'] = None
    return df

def backfill():
    weeks = _create_weeks()
    raw = pd.DataFrame()
    for week in weeks:
        d = load(week[1], week[0])
        raw = raw.append(d)
    clean = _scrub_bad_data(raw)
    return clean

if __name__ == '__main__':
    con = sqlite3.connect('data/football.db')
    cur = con.cursor()
    df = backfill()
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()
