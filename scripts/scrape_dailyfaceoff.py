from gazpacho import get, Soup
import pandas as pd

from common import META, CATEGORIES

url = 'https://www.dailyfaceoff.com/fantasy-hockey-projections/'
html = get(url)
soup = Soup(html)
skaters, goalies = soup.find("table", {"id": "igsv"})
sdf = pd.read_html(str(skaters))[0]
gdf = pd.read_html(str(goalies))[0]
df = pd.concat([sdf, gdf]).reset_index(drop=True)

column_mappings = {
    'Players': 'name',
    'TEAM': 'team',
    'POS.': 'position',
    'G': 'goals',
    'A': 'assists',
    '(+/-)': "plus_minus",
    'PPP': 'powerplay_points',
    'SOG': 'shots_on_goal',
    'HIT': 'hits',
    'BLK': 'blocks',
    'W': 'wins',
    'GAA': 'goals_against_average',
    'SV': 'saves',
    'SO': 'shutouts'
}

df = df.rename(columns=column_mappings)
df['source'] = 'Daily Faceoff'
df['fetched_at'] = pd.Timestamp('now')
df.loc[df['team'] == 'LAK', 'team'] = 'LA'
df.loc[df['team'] == 'VGK', 'team'] = 'VGS'
df.loc[df['team'] == 'NJD', 'team'] = 'NJ'
df.loc[df['team'] == 'SJS', 'team'] = 'SJ'
df.loc[df['team'] == 'TBL', 'team'] = 'TB'
df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
df = df[META + CATEGORIES]

df.to_csv("data/dailyfaceoff.csv", index=False)
