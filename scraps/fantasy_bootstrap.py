import sqlite3
import pandas as pd

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

# team lookups

team_codes = {
    'Patriots': 'NE',
    'Packers': 'GB',
    'Panthers': 'Car',
    'Eagles': 'Phi',
    'Seahawks': 'Sea',
    'Colts': 'Ind',
    'Redskins': 'Wsh',
    'Lions': 'Det',
    'Texans': 'Hou',
    'Vikings': 'Min',
    'Steelers': 'Pit',
    'Saints': 'NO',
    'Falcons': 'Atl',
    'Chiefs': 'KC',
    'Chargers': 'LAC',
    'Titans': 'Ten',
    '49ers': 'SF',
    'Bears': 'Chi',
    'Rams': 'LAR',
    'Bengals': 'Cin',
    'Dolphins': 'Mia',
    'Cowboys': 'Dal',
    'Jaguars': 'Jax',
    'Broncos': 'Den',
    'Giants': 'NYG',
    'Raiders': 'Oak',
    'Buccaneers': 'TB',
    'Browns': 'Cle',
    'Ravens': 'Bal',
    'Bills': 'Buf',
    'Cardinals': 'Ari',
    'Jets': 'NYJ'
}

team_codes_df = pd.DataFrame({
    'team': list(team_codes.keys()),
    'code': list(team_codes.values())
})

team_codes_df.to_sql('teams', con, if_exists='replace', index=False)
