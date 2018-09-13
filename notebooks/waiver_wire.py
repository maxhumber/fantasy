import sqlite3
from itertools import chain, cycle

import pandas as pd

con = sqlite3.connect('data/fantasy.db')
cur = con.cursor()

season = 2017

df = pd.read_sql(f'''
    select
    *
    from (
    	select
    	name,
    	position,
    	avg(points) as points,
    	count(*) as count
    	from projections
    	where
    	strftime('%Y-%m-%d', fetched_at) = (select max(strftime('%Y-%m-%d', fetched_at)) from projections)
    	group by 1, 2
    	having count(*) > 1
    	order by 3 desc
    ) projections
    left join (
    	select
    	*
    	from rosters
    	where
    	strftime('%Y-%m-%d', fetched_at) = current_date
    ) as rosters using (name, position)
    where
    (team is null or team = 'phantasy') and
    position in ('TE', 'WR', 'RB')
    ''', con)
    
