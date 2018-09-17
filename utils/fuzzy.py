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

TEAMS = [
    'Carolina Panthers',
    'New England Patriots',
    'Detroit Lions',
    'Pittsburgh Steelers',
    'Jacksonville Jaguars',
    'Washington Redskins',
    'Baltimore Ravens',
    'Chicago Bears',
    'New Orleans Saints',
    'Denver Broncos',
    'Seattle Seahawks',
    'Philadelphia Eagles',
    'Arizona Cardinals',
    'Los Angeles Rams',
    'Tennessee Titans',
    'Los Angeles Chargers',
    'Green Bay Packers',
    'Cincinnati Bengals',
    'Miami Dolphins',
    'Tampa Bay Buccaneers',
    'Dallas Cowboys',
    'Atlanta Falcons',
    'Kansas City Chiefs',
    'San Francisco 49ers',
    'New York Giants',
    'Indianapolis Colts',
    'Buffalo Bills',
    'Oakland Raiders',
    'Minnesota Vikings',
    'New York Jets',
    'Cleveland Browns',
    'Houston Texans'
]

ALL = (
    pd.concat([PLAYERS, pd.DataFrame({'name': TEAMS})], sort=False)
    .fillna('DEF')
    .reset_index(drop=True)
)

def fuzzy_full(name, names):
    match = process.extract(name, choices=names, scorer=fuzz.partial_ratio)[0][0]
    return match

def fuzzy_half(name, names):
    options = process.extract(name, choices=names, scorer=fuzz.partial_token_sort_ratio)
    possible_matches = [
        option for option in options
        if (option[0][0] == name[0]) and
        # just keep the first last name before the hyphen
        option[0].split(' ')[1].split('-')[0] == name.split('. ')[1]
    ]
    try:
        match = possible_matches[0]
    except IndexError:
        return name
    if match[1] > 70:
        return match[0]
    else:
        return name

def fuzzy_lookup(name, position, abbreviated=False):
    names = list(ALL[ALL['position'] == position]['name'].values)
    if name in names:
        return name
    try:
        if abbreviated:
            return fuzzy_half(name, names)
        else:
            return fuzzy_full(name, names)
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
