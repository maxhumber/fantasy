import re
import time
import warnings
from bs4 import BeautifulSoup
import pandas as pd
import requests

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# COMMON #

META = [
    'name',
    'team',
    'position',
    'source',
    'fetched_at'
]

CATEGORIES = [
    'goals',
    'assists',
    'plus_minus',
    'powerplay_points',
    'shots_on_goal',
    'hits',
    'blocks',
    'wins',
    'goals_against_average',
    'saves',
    'save_percentage',
    'shutouts'
]

# DAILY FACEOFF #

def scrape_daily_faceoff():
    URL = 'https://www.dailyfaceoff.com/fantasy-hockey-projections/'
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.DataFrame()
    for id in ['igsv', 'igsv-1']:
        table = soup.find('table', {'id': f'{id}-1N8XNZpOIb8-6WcOPANqSHRyHBXlwZ6X_1vgGyDbETm4'})
        df = df.append(pd.read_html(str(table))[0])
    df = df.reset_index(drop=True)
    return df

def clean_daily_faceoff(df):
    # fix skaters name
    df.loc[df['Name'].isnull(), 'Name'] = df['SKATERS']
    column_mappings = {
        'RANK': 'rank',
        'Name': 'name',
        'TEAM': 'team',
        'POS': 'position',
        'Pos. Rank': 'goalie',
        'G': 'goals',
        'A': 'assists',
        'PPP': 'powerplay_points',
        'SOG': 'shots_on_goal',
        'HIT': 'hits',
        'BLK': 'blocks',
        'W': 'wins',
        'GAA': 'goals_against_average',
        'SV%': 'save_percentage',
    }
    df = df.rename(columns=column_mappings)
    df = df[column_mappings.values()]
    # fix goalie problem
    df.loc[df['goalie'] == 'G', 'team'] = df['position']
    df.loc[df['goalie'] == 'G', 'position'] = df['goalie']
    # add null columns
    df['saves'] = None
    df['plus_minus'] = None
    df['shutouts'] = None
    # add metadata
    df['source'] = 'Daily Faceoff'
    df['fetched_at'] = pd.Timestamp('now')
    # fix team names
    df.loc[df['team'] == 'LAK', 'team'] = 'LA'
    df.loc[df['team'] == 'VGK', 'team'] = 'VGS'
    df.loc[df['team'] == 'NJD', 'team'] = 'NJ'
    df.loc[df['team'] == 'SJS', 'team'] = 'SJ'
    df.loc[df['team'] == 'TBL', 'team'] = 'TB'
    # fix claude
    df.loc[df['position'] == 'C/LW/RW', 'team'] = 'LW/RW'
    # format
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df = df[META + CATEGORIES]
    return df

def daily_faceoff():
    df = scrape_daily_faceoff()
    df = clean_daily_faceoff(df)
    return df

# CBS #

def scrape_position_cbs(position):
    url = f'https://www.cbssports.com/fantasy/hockey/stats/{position}/2019/season/projections/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'TableBase-table'})
    pdf = pd.read_html(str(table))[0]
    return pdf

def scrape_cbs():
    df = pd.DataFrame()
    for position in ['C', 'W', 'D', 'G']:
        pdf = scrape_position_cbs(position)
        df = df.append(pdf)
        time.sleep(0.5)
    df = df.reset_index(drop=True)
    return df

def parse_name_cbs(x):
    x = re.split("\s\s[A-Z]{1,2}\s\s[A-Z]{2,3}\s\s", x)[-1]
    position = re.search('\s[A-Z]{1,2}\s', x).group(0)
    name, team = re.split("\s[A-Z]{1,2}\s", x)
    return name.strip(), team.strip(), position.strip()

def clean_cbs(df):
    column_mappings = {
        'Player': 'player',
        'g  Goals': 'goals',
        'a  Assists': 'assists',
        'sog  Shots on Goal': 'shots_on_goal',
        '+/-  Plus-Minus Goals Scored For Or Against Total': 'plus_minus',
        'ppg  Powerplay Goals': 'powerplay_points',
        'sv  Saves': 'saves',
        'gaa  Goals Against Average': 'goals_against_average',
        'so  Shutouts': 'shutouts',
        'w  Wins': 'wins'
    }
    df = df.rename(columns=column_mappings)
    df = df[list(column_mappings.values())]
    meta = pd.DataFrame(list(df.player.apply(parse_name_cbs)), columns=['name', 'team', 'position'])
    df = pd.concat([meta, df], axis=1)
    # add missing categories
    df['hits'] = None
    df['blocks'] = None
    df['save_percentage'] = None
    # add metadata
    df['source'] = 'CBS'
    df['fetched_at'] = pd.Timestamp('now')
    # fix teams
    df.loc[df['team'] == 'LV', 'team'] = 'VGS'
    df.loc[df['team'] == 'WAS', 'team'] = 'WSH'
    # format
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df = df[META + CATEGORIES]
    return df

def cbs():
    df = scrape_cbs()
    df = clean_cbs(df)
    return df

# NUMBERFIRE #

def scrape_position_numberfire(position):
    url = f'https://www.numberfire.com/nhl/fantasy/yearly-projections/{position}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all('table', {'class':'projection-table'})
    names = pd.read_html(str(tables[0]))[0]
    data = pd.read_html(str(tables[1]))[0]
    df = pd.concat([names, data], axis=1)
    return df

def scrape_numberfire():
    df = pd.DataFrame()
    for position in ['skaters', 'goalies']:
        df = df.append(scrape_position_numberfire(position))
    df = df.reset_index(drop=True)
    return df

def parse_name_numberfire(x):
    name = re.split("\s[A-Z]\.", x)[0]
    x = x.split('(')[1].replace(')', '')
    position, team = x.split(', ')
    return name, team, position

def clean_numberfire(df):
    column_mappings = {
        'Player': 'player',
        'G': 'goals',
        'A': 'assists',
        '+/-': 'plus_minus',
        'PPA': 'powerplay_assists',
        'PPG': 'powerplay_goals',
        'Shots': 'shots_on_goal',
        'Win': 'wins',
        'GAA': 'goals_against_average',
        'SV': 'saves',
        'SV%': 'save_percentage'
    }
    df = df.rename(columns=column_mappings)
    df = df[column_mappings.values()]
    meta = pd.DataFrame(list(df.player.apply(parse_name_numberfire)), columns=['name', 'team', 'position'])
    df = pd.concat([meta, df], axis=1)
    df['powerplay_points'] = df['powerplay_assists'] + df['powerplay_goals']
    df['save_percentage'] = df['save_percentage'].str.replace('%', '')
    # add missing
    df['hits'] = None
    df['blocks'] = None
    df['shutouts'] = None
    # add metadata
    df['source'] = 'numberFire'
    df['fetched_at'] = pd.Timestamp('now')
    # format
    df[CATEGORIES] = df[CATEGORIES].apply(pd.to_numeric, errors='coerce')
    df = df[META + CATEGORIES]
    return df

def numberfire():
    df = scrape_numberfire()
    df = clean_numberfire(df)
    return df

def fetch_all():
    df = pd.DataFrame()
    df = df.append(daily_faceoff())
    df = df.append(cbs())
    df = df.append(numberfire())
    df = df.reset_index(drop=True)
    return df

# YAHOO DRAFT RANKINGS #

def yahoo_draft_rankings():
    URL = 'https://www.fantasypros.com/nhl/adp/overall.php'
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'lxml')
    df = pd.read_html(str(soup.find_all('table')[0]))[0]
    df[['first', 'last', 'team']] = df['Player Team'].str.split(' ', n=2, expand=True)
    df['name'] = df['first'] + ' ' + df['last']
    df.columns = [c.lower() for c in df.columns]
    df = df[['name', 'yahoo']]
    return df

# CAPFRIENDLY #

def capfriendly():
    df = pd.DataFrame()
    for page in range(1, 10+1):
        url = f'https://www.capfriendly.com/browse/active/2020/salary&hide=team,clauses,position,handed,expiry-status,caphit,skater-stats,goalie-stats&p={page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        pdf = pd.read_html(str(soup.find('table')))[0]
        df = df.append(pdf)
        time.sleep(0.5)
    df['PLAYER'] = df['PLAYER'].apply(lambda x: re.split("\d{1}|\d{2}|\d{3}", x)[-1].replace('. ', ''))
    df['SALARY'] = df['SALARY'].apply(lambda x: x.replace('$', '').replace(',', ''))
    df['SALARY'] = df['SALARY'].apply(float)
    df.columns = ['name', 'age', 'salary']
    df = df.reset_index(drop=True)
    return df
