import pandas as pd

dd = pd.read_csv("draft/data/projections_dfo_d.csv", skiprows=14)
df = pd.read_csv("draft/data/projections_dfo_f.csv", skiprows=14)
dg = pd.read_csv("draft/data/projections_dfo_g.csv", skiprows=12)

column_mappings = {
    "Players": "name",
    "TEAM": "team",
    "Pos": "position",
    'Age': "age",
    'G': "goals",
    'A': "assists",
    'PTS': "points",
    '(+/-)': "plus_minus",
    'PPP': "powerplay_points",
    'GWG': "game_winning_goals",
    'SOG': "shots_on_goal",
    'BLK': "blocks",
    'HIT': "hits"
}

columns = [
    'name',
    'team',
    'position',
    'age',
    'goals',
    'assists',
    'points',
    'plus_minus',
    'powerplay_points',
    'game_winning_goals',
    'shots_on_goal',
    'blocks',
    'hits',
]

dd = dd.rename(columns=column_mappings)
dd = dd[columns]

df = df.rename(columns=column_mappings)
df = df[columns]

goalie_mappings = {
    'Players': "name",
    'TEAM': "team",
    'POS.': "position",
    'AGE': "age",
    'W': "wins",
    'SO': "shutouts",
    'SV': "saves",
    'GA': "goals_allowed",
    'SA': "shots_against",
    'SV%': "save_percentage",
    'GAA': "goals_against_average"
}

dg = dg.rename(columns=goalie_mappings)

dg = dg[[
    'name',
    'team',
    'position',
    'age',
    'wins',
    'shutouts',
    'save_percentage',
    "saves"
]]

df = pd.concat([df, dd, dg])

df.to_csv("draft/data/projections-dfo.csv", index=False)
