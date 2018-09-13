import pandas as pd
import sqlite3
from weekly import espn, fantasy_pros, fantasy_sharks, numberfire
from active import players, rosters
from utils.week import week
from utils.fuzzy import fuzzy_defense, fuzzy_lookup

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

def fetch(week):
    data_espn = espn.load(week)
    data_fantasy_pros = fantasy_pros.load(week)
    data_fantasy_sharks = fantasy_sharks.load(week)
    data_numberfire = numberfire.load(week)
    df = pd.concat([data_espn, data_fantasy_pros, data_fantasy_sharks, data_numberfire])
    df = df.reset_index(drop=True)
    # fix defense naming problem across sources
    df.loc[df['position'] == 'DEF', 'name'] = (
        df['name'].apply(lambda team: fuzzy_defense(team))
    )
    return df

active_rosters = rosters.load()

def _filter(df, position):
    return list(df[df['position'] == position]['name'].values)

# def fix_rosters():
active_players = players.fetch()
df['name'] = df.apply(lambda row: fuzzy_lookup(row['name'], row['position']), axis=1)

df['name'] = df.apply(lambda row: fuzzy_lookup(row['name'], _filter(players, 'QB'), row['position']), axis=1)


if __name__ == '__main__':
    # pull all
    projections_all = fetch(week='all')
    projections_all.to_sql('projections', con, if_exists='append')
    # pull this week
    projections_week = fetch(week)
    projections_week.to_sql('projections', con, if_exists='append')


    active_players = players.fetch()
