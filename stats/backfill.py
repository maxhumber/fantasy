import sqlite3
from itertools import product

import pandas as pd

from stats.points import load

def backfill(start, end):
    weeks = list(product(range(start, end + 1), range(1, 17 + 1)))
    df = pd.DataFrame()
    for week in weeks:
        print(week)
        d = load(week[1], week[0])
        df = df.append(d, sort=False)
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = backfill(2015, 2017)
    df.to_sql('points', con, if_exists='replace', index=False)
    con.commit()
    con.close()
