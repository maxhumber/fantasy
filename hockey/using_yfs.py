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

### get roster

import pandas as pd
from collections import ChainMap

league_id = 74371
team_id = 3
end_point = f'team/nhl.l.{league_id}.t.{team_id}/roster/players'
data = api.get(end_point)

# clean

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

players = data['fantasy_content']['team'][1]['roster']['0']['players']
keys = [k for k in players.keys() if k != 'count']
players = [clean_player(players[k]) for k in keys]
pd.DataFrame(players)

#
