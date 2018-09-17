import sqlite3

import pandas as pd
from fuzzywuzzy import process, fuzz

def _fetch_players():
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    players = pd.read_sql('select name, position from players', con)
    con.close()
    return players

PLAYERS = _fetch_players()

def fuzzy_lookup(name, position):
    names = list(PLAYERS[PLAYERS['position'] == position]['name'].values)
    if name in names:
        return name
    try:
        match = process.extract(name, choices=names, scorer=fuzz.partial_ratio)[0]
        return match[0] if match[1] > 70 else name
    except IndexError:
        return name

def fuzzy_cleanup(df):
    fuzzy_names = df[df['fuzzy_name'].duplicated()]['fuzzy_name'].values
    bad = df[df['fuzzy_name'].isin(fuzzy_names)]
    bad = bad[bad['fuzzy_name'] != bad['name']]['name'].values
    df = df[~df['name'].isin(bad)]
    df = df.drop('name', axis=1)
    df = df.rename(columns={'fuzzy_name': 'name'})
    return df
