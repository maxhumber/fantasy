import pandas as pd
import sqlite3
import altair as alt
from sklearn.metrics import (
    r2_score,
    explained_variance_score,
    mean_absolute_error,
    mean_squared_error
)
import math

con = sqlite3.connect('projections.db')
cur = con.cursor()

df = pd.read_sql('''
    select
    name,
    position,
    round(projections.points, 1) as projected,
    round(actuals.points, 1) as actual,
    actuals.points - projections.points as over_under
    from (
        select
        name,
        position,
        round(avg(points), 1) as points,
        (round(min(points), 1) || '-' || round(max(points), 1)) as range,
        count(*) as count
        from projections
        where week = 1
        group by 1, 2
        having count(*) > 1
        order by 3 desc
    ) projections
    left join actuals using (name, position)
    where actuals.points is not null
''', con)

line_df = pd.DataFrame({'projected': range(0, 40, 1), 'actual': range(0, 40, 1)})

points = (alt
    .Chart(df)
    .mark_circle(opacity=1/2)
    .encode(
        x='projected',
        y='actual',
        color='position',
        tooltip=['name']
    )
    .interactive()
)
line = alt.Chart(line_df).mark_line().encode(x='projected', y='actual')
(points + line).properties(
    height=500,
    width=600,
    background='white')

x = df['actual']
y = df['projected']

r2_score(x, y)
explained_variance_score(x, y)
mean_absolute_error(x, y)
math.sqrt(mean_squared_error(x, y))
