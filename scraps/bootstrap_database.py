import sqlite3
from itertools import product
import pandas as pd

con = sqlite3.connect('nfl.db')
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

# generate all slot and offset combinations

def expand_grid(dictionary):
    return pd.DataFrame(
        [row for row in product(*dictionary.values())],
        columns=dictionary.keys()
    )

# pmap = {'QB': 0, 'RB': 2, 'WR': 4, 'TE': 6, 'DEF': 16, 'K': 17}
# step = 40

def create_combos(pmap, step=40):
    combos = {
        'slot': list(pmap.values()),
        'offset': list(range(0, 300, step))
    }
    combos = expand_grid(combos)
    combos = pd.concat([
        combos[combos['offset'] < 40],
        combos[combos['slot'] == pmap['WR']],
        combos[combos['slot'] == pmap['RB']]
    ]).sort_values(['slot', 'offset'])
    combos = combos.drop_duplicates().reset_index(drop=True)
    return combos

combos = create_combos()
combos.to_sql('combos', con, if_exists='replace', index=False)
