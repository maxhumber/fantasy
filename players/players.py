import sqlite3
import pandas as pd
from draft.adp import scrape_seasons

if __name__ == '__main__':
    con = sqlite3.connect('data/fantasy.db')
    cur = con.cursor()
    df = scrape_seasons(start=2015, end=2018)
    df = df[['name', 'position']].drop_duplicates().sort_values(['position', 'name'])
    df['fetched_at'] = pd.Timestamp('now')
    df.to_sql('players', con, if_exists='replace', index=False)
    con.commit()
    con.close()
