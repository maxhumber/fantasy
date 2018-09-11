from fuzzywuzzy import process, fuzz

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

def fuzzy_defence(team):
    return process.extract(team, choices=TEAMS, scorer=fuzz.partial_ratio)[0][0]

def fuzzy_lookup(name, names, position):
    if position == 'DEF':
        return process.extract(team, choices=TEAMS, scorer=fuzz.partial_ratio)[0][0]
    try:
        match = process.extract(name, choices=names, scorer=fuzz.partial_token_sort_ratio)[0]
        if match[1] > 75:
            return match[0]
        else:
            return name
    except IndexError:
        return name
