import re
import time
import warnings

from gazpacho import get, Soup
import pandas as pd

from common import META, CATEGORIES

def scrape(position, year=2020):
    url = f'https://www.cbssports.com/fantasy/hockey/stats/{position}/{year}/season/projections/'
    html = get(url)
    soup = Soup(html)
    table = soup.find('table', {'class': 'TableBase-table'})
    pdf = pd.read_html(str(table))[0]
    return pdf

df = pd.DataFrame()

for position in ['C', 'W', 'D', 'G']:
    pdf = scrape(position)
    df = df.append(pdf)
    time.sleep(0.5)

df = df.reset_index(drop=True)

def fix_name(x):
    x = re.split("\s\s[A-Z]{1,2}\s\s[A-Z]{2,3}\s\s", x)[-1]
    position = re.search('\s[A-Z]{1,2}\s', x).group(0)
    name, team = re.split("\s[A-Z]{1,2}\s", x)
    return name.strip(), team.strip(), position.strip()

meta = pd.DataFrame(list(df['Player'].apply(fix_name)), columns=['name', 'team', 'position'])
df = pd.concat([meta, df], axis=1)

column_mappings = {
    'Player': 'player',
    'g  Goals': 'goals',
    'a  Assists': 'assists',
    '+/-  Plus-Minus Goals Scored For Or Against Total': 'plus_minus',
    'ppg  Powerplay Goals': 'powerplay_points',
    'sog  Shots on Goal': 'shots_on_goal',
    'w  Wins': 'wins',
    'gaa  Goals Against Average': 'goals_against_average',
    'sv  Saves': 'saves',
    'so  Shutouts': 'shutouts'
}

df = df.rename(columns=column_mappings)
df['hits'] = None
df['blocks'] = None
df['source'] = 'CBS'
df['fetched_at'] = pd.Timestamp('now')
df.loc[df['team'] == 'LV', 'team'] = 'VGS'
df.loc[df['team'] == 'WAS', 'team'] = 'WSH'
df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
df = df[META + CATEGORIES]

df.to_csv("data/cbs.csv", index=False)
