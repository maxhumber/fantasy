OFFENSE = {
    'passing_yards': 1/25,
    'passing_touchdowns': 4,
    'passing_interceptions': -2,
    'rushing_yards': 1/10,
    'rushing_touchdowns': 6,
    'receiving_yards': 1/10,
    'receiving_touchdowns': 6,
    'fumble_touchdowns': 6,
    'fumbles_lost': -2,
    'two_point_conversions': 2,
}

KICKING = {
    'extra_points_made': 1,
    'field_goals_made': 3,
    'field_goals_made_over_50': 5
}

DEFENSE = {
    'sacks': 1,
    'interceptions': 2,
    'safeties': 2,
    'fumble_recoveries': 2,
    'touchdowns': 6
}

POINTS_ALLOWED = {
    0: 10,
    6: 7,
    13: 4,
    20: 1,
    27: 0,
    34: -1,
    999: -4
}

def score_offense(row):
    points = 0
    for rule, value in OFFENSE.items():
        points += row[rule] * value
    return points

def score_kicking(row):
    points = 0
    for rule, value in KICKING.items():
        points += row[rule] * value
    return points

def score_defense(row):
    points = 0
    for rule, value in DEFENSE.items():
        points += row[rule] * value
    points_allowed = row['points_allowed']
    points += [v for k, v in POINTS_ALLOWED.items() if k >= points_allowed][0]
    return points

def score(row):
    if row.position in ('QB', 'RB', 'WR', 'TE'):
        return score_offense(row)
    elif row.position == 'K':
        return score_kicking(row)
    elif row.position == 'DEF':
        return score_defense(row)
    else:
        return None
