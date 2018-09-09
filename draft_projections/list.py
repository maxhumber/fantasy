import pandas as pd
import sqlite3

con = sqlite3.connect('fantasy.db')
cur = con.cursor()

sql = '''
    select
    *
    from value_over_replacement as vor
    left join meta_scout_fantasy as meta on meta.name = vor.name
    left join adp_nfl as nfl on nfl.name = vor.name
'''

df = pd.read_sql(sql, con)
df.to_excel('list.xlsx', index=False)
