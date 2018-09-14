import sqlite3
import pandas as pd
from fuzzywuzzy import process, fuzz

def _fetch_players():
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    players = pd.read_sql('select * from players', con)
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

def fuzzy_defense(team):
    return process.extract(team, choices=TEAMS, scorer=fuzz.partial_ratio)[0][0]

# diagnostics
# position = 'TE'
# names = list(PLAYERS[PLAYERS['position'] == position]['name'].values)
# name = 'J. Graham'

def fuzzy_player(name, names):
    options = process.extract(name, choices=names, scorer=fuzz.partial_token_sort_ratio)
    # option = options[0]
    possible_matches = [
        option
        for option in options
        if (option[0][0] == name[0]) and
        # last name and then remove after hyphen
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

def fuzzy_lookup(name, position):
    names = list(PLAYERS[PLAYERS['position'] == position]['name'].values)
    if position == 'DEF':
        return fuzzy_defense(name)
    else:
        return fuzzy_player(name, names)
