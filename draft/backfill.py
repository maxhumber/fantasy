import sqlite3
import pandas as pd
from draft.adp import load

COLUMNS = 'name,position,team,points,std,min,max,bye,injury,age,adp,season'.split(',')

def backfill(start, end):
    seasons = range(start, end + 1)
    df = pd.DataFrame(columns=COLUMNS)
    for season in seasons:
        d = load(season)
        df = df.append(d, sort=False)
    return df

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df_back = backfill(2015, 2017)
    df_draft = pd.read_csv('draft/draft.csv')
    df_draft = pd.merge(df_draft, load(2018), how='left', on='name')
    df_draft['season'] = 2018
    df = pd.concat([df_back, df_draft])
    df.to_sql('draft', con, if_exists='replace', index=False)
    con.commit()
    con.close()
