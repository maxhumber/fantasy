import sqlite3

import schedule
import pandas as pd

from fantasy.projections import espn
from fantasy.projections import fantasy_pros
from fantasy.projections import fantasy_sharks
from fantasy.projections import numberfire

from fantasy.utils.week import week

def load_projections(week):
    df = pd.concat([
        espn.load(week),
        fantasy_pros.load(week),
        fantasy_sharks.load(week),
        numberfire.load(week)
    ])
    return df

def to_database(week):
    con = sqlite3.connect('data/football.db')
    df = load_projections(week)
    df.to_sql('projections', con, if_exists='append', index=False)
    con.commit()
    con.close()

if __name__ == '__main__':
    to_database(week)
