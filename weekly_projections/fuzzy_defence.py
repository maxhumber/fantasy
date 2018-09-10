import pandas as pd
import sqlite3
from fuzzywuzzy import process, fuzz

pd.set_option('display.max_rows', 999)


con = sqlite3.connect('projections.db')
cur = con.cursor()

df = pd.read_sql("select * from projections where position = \'DEF\'", con)

teams = list(df.query('source == "Fantasy Sharks"')['name'].values)

fuzz.partial_ratio('Bears', 'Chicago Bears')
fuzz.ratio('Bears', 'Chicago Bears')
process.extract('Bears', choices=teams, scorer=fuzz.partial_ratio)
process.extract('Bears', limit=1, choices=teams, scorer=fuzz.partial_ratio)[0][0]

help(process.extract)

df['name2'] = (
    df['name']
    .apply(lambda team:
        process.extract(team, limit=1, choices=teams, scorer=fuzz.partial_ratio)[0][0]
    )
)
df[['name', 'name2']].sort_values('name2')



#
