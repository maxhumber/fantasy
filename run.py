import pandas as pd
import sqlite3
from weekly import espn, fantasy_pros, fantasy_sharks, numberfire
from utils.week import week
from utils.fuzzy import fuzzy_defence

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

data_espn = espn.load(week)
data_fantasy_pros = fantasy_pros.load(week)
data_fantasy_sharks = fantasy_sharks.load(week)
data_numberfire = numberfire.load()  # payload doesn't accept a week argument

df = pd.concat([data_espn, data_fantasy_pros, data_fantasy_sharks, data_numberfire])
df = df.reset_index(drop=True)
df.loc[df['position'] == 'DEF', 'name'] = (
    df['name'].apply(lambda team: fuzzy_defence(team))
)

df.to_sql('projections', con, if_exists='append')
