# https://developer.yahoo.com/fantasysports/guide/league-resource.html#league-resource-key_format

from yfs import API
import json

with open('hockey/app.json', 'r') as f:
    app = json.load(f)

client_id = app['client_id']
client_secret = app['client_secret']
league_id = 74371

api = API(client_id, client_secret, league_id)

# examples

api.get('league/nhl.l.74371/settings')
api.get('team/nhl.l.74371.t.3/roster/players')
api.get('league/nhl.l.74371/teams')
api.get('league/386.l.74371/settings')
api.get('game/386/players')
api.get('game/nhl')

# manual

import json
import os
import requests
import webbrowser

authorize_url = 'https://api.login.yahoo.com/oauth2/request_auth'
access_token_url = 'https://api.login.yahoo.com/oauth2/get_token'

redirect_uri = 'oob'
league_id = 74371
base_url = 'https://fantasysports.yahooapis.com/fantasy/v2'

### get initial tokens

params = {
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'language': 'en-us',
}

headers = {'Content-Type': 'application/json'}
response = requests.post(authorize_url, params=params, headers=headers)

webbrowser.open(response.url)
code = input('Enter code: ')

data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'code': code,
    'grant_type': 'authorization_code',
}

response = requests.post(access_token_url, data=data)

### set tokens

data = response.json()
access_token = data['access_token']
refresh_token = data['refresh_token']

### refresh tokens

data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token',
}

response = requests.post(access_token_url, data=data)

data = response.json()
access_token = data['access_token']
refresh_token = data['refresh_token']

### get roster

from collections import ChainMap

league_id = 74371
team_id = 3
url = base_url + '/' + f'team/nhl.l.{league_id}.t.{team_id}/roster/players'

response = requests.get(url, params={'format':'json'}, headers={'Authorization': f'Bearer {access_token}'})
data = response.json()

players = data['fantasy_content']['team'][1]['roster']['0']['players']
players['0']

player = players['0']['player'][0]
player = dict(ChainMap(*player))

player = players['3']

def clean_player(player):
    player = player['player'][0]
    player = dict(ChainMap(*player))
    player = {
        'id': player['player_id'],
        'name': player['name']['full'],
        'position': [list(d.values())[0] for d in player['eligible_positions']],
        'team_name': player['editorial_team_full_name'],
        'team_code': player['editorial_team_abbr']
    }
    return player

keys = [k for k in players.keys() if k != 'count']

import pandas as pd
pd.DataFrame([clean_player(players[k]) for k in keys])

clean_player(players['3'])

#
