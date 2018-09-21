import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.preprocessing import LabelBinarizer, StandardScaler
from sklearn.exceptions import DataConversionWarning
import mord
from sklearn_pandas import DataFrameMapper
import altair as alt
import warnings

from hockey.utils import CATEGORIES

warnings.filterwarnings("ignore", category=DataConversionWarning)
pd.options.display.float_format = '{:20,.4f}'.format

con = sqlite3.connect('hockey/hockey.db')

# fetch

df = pd.read_sql('select * from projections where season = "2018-19"', con).fillna(0)
df = df.groupby(['season', 'name', 'position'])[CATEGORIES].mean().reset_index()
ranks = pd.read_sql('''
    select
    name,
    rank
    from ranks
    ''', con)
df = pd.merge(ranks, df, how='left', on=['name'])
df = df.drop(['name', 'season'], axis=1)
df['rank'] = pd.to_numeric(df['rank'])
# GAA is a bad thing, need to reverse
df['goals_against_average'] = -df['goals_against_average']
df = df.dropna()

# split

target = 'rank'
y = df[target].values
X = df.drop(target, axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

# prep

mapper = DataFrameMapper([
    ('position', LabelBinarizer()),
    (['goals'], StandardScaler()),
    (['assists'], StandardScaler()),
    (['plus_minus'], StandardScaler()),
    (['powerplay_points'], StandardScaler()),
    (['shots_on_goal'], StandardScaler()),
    (['hits'], StandardScaler()),
    (['blocks'], StandardScaler()),
    (['wins'], StandardScaler()),
    (['goals_against_average'], StandardScaler()),
    (['saves'], StandardScaler()),
    (['save_percentage'], StandardScaler()),
    (['shutouts'], StandardScaler())
],
df_out=True)

X_train_m = mapper.fit_transform(X_train)
X_test_m = mapper.transform(X_test)

# model

model = mord.OrdinalRidge(fit_intercept=False)
model.fit(X_train_m, y_train)

# evaluate

compare = pd.DataFrame({
    'true': y_test,
    'pred': model.predict(X_test_m)
})

alt.Chart(compare, background='white').mark_point().encode(x='true', y='pred')
r2_score(compare['true'], compare['pred'])

# features

bias = pd.DataFrame({
    'feature': mapper.transformed_names_,
    'coef': model.coef_
}).sort_values('coef')

bias['calculated_at'] = pd.Timestamp('now')
bias.to_sql('bias', con, if_exists='replace', index=False)

X_train_m.describe().T

# explore

df[df['position'] != 'G'][CATEGORIES].mean()

model.predict(
    mapper.transform(
    pd.DataFrame([{
        'position': 'C',
        'goals': 21,
        'assists': 34,
        'plus_minus': 3,
        'powerplay_points': 8,
        'shots_on_goal': 90,
        'hits': 34,
        'blocks': 25,
        'wins': 0.0,
        'goals_against_average': 0.0,
        'saves': 0.0,
        'save_percentage': 0.0,
        'shutouts': 0.0
        }])
    )
)[0]

df[df['position'] == 'G'][CATEGORIES].mean().to_dict()
