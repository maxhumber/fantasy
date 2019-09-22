# https://developer.yahoo.com/fantasysports/guide/league-resource.html#league-resource-key_format

from yfs import API
import json
import pandas as pd
from collections import ChainMap
import copy

with open('hockey/app.json', 'r') as f:
    app = json.load(f)

client_id = app['client_id']
client_secret = app['client_secret']
league_id = 74371

api = API(client_id, client_secret, league_id)
api.refresh_tokens()

# utilities

def _flatten(list_of_dicts):
    list_of_dicts = [d for d in list_of_dicts if d != []]
    return dict(ChainMap(*list_of_dicts))

# get league metadata

def get_metadata(league_id):
    data = api.get(f'league/nhl.l.{league_id}/metadata')
    return data['fantasy_content']['league'][0]

get_metadata(league_id)

# get teams

def _clean_team(team):
    team = _flatten(team['team'][0])
    manager = [list(d.values())[0]['nickname'] for d in team['managers']]
    team = {
        'id': team['team_id'],
        'name': team['name'],
        'manager': manager
    }
    return team

def get_teams(league_id):
    teams = api.get(f'league/nhl.l.{league_id}/teams')
    teams = teams['fantasy_content']['league'][1]['teams']
    ids = [k for k in teams.keys() if k != 'count']
    teams = [_clean_team(teams[id]) for id in ids]
    return teams

pd.DataFrame(get_teams(league_id=74371))

# get roster

def _clean_player(player):
    player = _flatten(player['player'][0])
    position = [list(d.values())[0] for d in player['eligible_positions']]
    player = {
        'id': player['player_id'],
        'name': player['name']['full'],
        'position': position,
        'team': player['editorial_team_full_name'],
    }
    return player

def get_roster(team_id, league_id):
    end_point = f'team/nhl.l.{league_id}.t.{team_id}/roster/players'
    data = api.get(end_point)
    players = data['fantasy_content']['team'][1]['roster']['0']['players']
    ids = [k for k in players.keys() if k != 'count']
    players = [{**_clean_player(players[id]), **{'team_id': team_id}} for id in ids]
    return players

pd.DataFrame(get_roster(team_id=3, league_id=74371))

# get all rosters

teams = [team['id'] for team in get_teams(league_id=74371)]
rosters = pd.DataFrame()
for team_id in teams:
    roster = pd.DataFrame(get_roster(team_id=team_id, league_id=74371))
    rosters = rosters.append(roster)


# get full season stats

def _map_stats(stats):
    mapping = {
        '1': 'goals',
        '14': 'shots_on_goal',
        '19': 'wins',
        '2': 'assists',
        '23': 'goals_allowed_average',
        '25': 'saves',
        '26': 'save_percentage',
        '27': 'shutouts',
        '31': 'hits',
        '32': 'blocks',
        '4': 'plus_minus',
        '8': 'powerplay_points'
    }
    return {
        mapping[k]: v
        for k, v in stats.items()
        if k not in ['22', '24']
    }

def _clean_stats(stats):
    stats_ = {}
    for i in range(len(stats)):
        key = stats[i]['stat']['stat_id']
        value = float(stats[i]['stat']['value'])
        stats_[key] = value
    stats_ = _map_stats(stats_)
    return stats_

def get_stats(league_id):
    standings = api.get(f'league/nhl.l.{league_id}/standings')
    standings = standings['fantasy_content']['league'][1]['standings'][0]['teams']
    keys = [k for k in standings.keys() if k != 'count']
    teams = {}
    for key in keys:
        team_name = _flatten(standings[key]['team'][0])['name']
        stats = standings[key]['team'][1]['team_stats']['stats']
        stats = _clean_stats(stats)
        teams[team_name] = stats
    return teams

# simulate a week

teams = get_teams(league_id=74371)
teams = [team['name'] for team in teams]
# teams.remove('fantasy.py')
stats = get_stats(league_id=74371)

def simulate_score(home, away, stats, verbose=False):
    s = copy.deepcopy(stats)
    home_categories = s[home]
    away_categories = s[away]
    wins = 0
    ties = 0
    losses = 0
    for category, v in home_categories.items():
        # print(f'{category}: {v} | {away_categories[category]}')
        if category == 'goals_allowed_average':
            v, away_categories[category] = -v, -away_categories[category]
        if v == away_categories[category]:
            ties += 1
        elif v > away_categories[category]:
            wins += 1
        else:
            losses += 1
    if verbose:
        print(f'{home} vs. {away}: {wins}-{ties}-{losses}')
    return wins, ties, losses

def simulate_all_matchups(team, teams, stats, verbose=False):
    wins = 0
    ties = 0
    losses = 0
    for away in teams:
        if team == away:
            continue
        w, t, l = simulate_score(team, away, stats, verbose)
        if w == l:
            ties += 1
        elif w > l:
            wins += 1
        else:
            losses += 1
    print(f'{team}: {wins}-{ties}-{losses}')

simulate_all_matchups('Subban Hussein', teams, stats)
simulate_all_matchups('Bee-ware🐝', teams, stats)

for team in teams:
    simulate_all_matchups(team, teams, stats)

simulate_score('fantasy.py', '#FreeWilly', stats)



stats = pd.DataFrame(get_stats(league_id=74371)).T
stats['goals_allowed_average'] = -stats['goals_allowed_average']
stats_ranks = stats.rank(ascending=False)
stats_ranks.T.mean()


# get standings

def get_standings(league_id):
    standings = api.get(f'league/nhl.l.{league_id}/standings')
    standings = standings['fantasy_content']['league'][1]['standings'][0]['teams']
    keys = [k for k in standings.keys() if k != 'count']
    teams = {}
    team = '0'
    for key in keys:
        team_name = _flatten(standings[key]['team'][0])['name']
        team_standings = standings[key]['team'][2]['team_standings']
        outcomes = team_standings['outcome_totals']
        team_standings.pop('outcome_totals')
        team_standings = {**team_standings, **outcomes}
        teams[team_name] = team_standings
    return teams

pd.DataFrame(get_standings(league_id=74371))






#####

player_id = 3982
api.get(f'player/nhl.p.{player_id}/ownership')

player_id = 3982
league/nhl.l.{league_id}/players;search=letang/ownership
league/nhl.l.{league_id}/players;search=letang/stats

api.get(f'league/nhl.l.{league_id}/players;search=letang/stats')


#####

api.get(f'league/nhl.l.{league_id}/scoreboard')


#### Draft Results

data = api.get(f'league/nhl.l.{league_id}/draftresults')
draft = data['fantasy_content']['league'][1]['draft_results']

results = []
for key in draft.keys():
    try:
        pick = draft[key]['draft_result']
        result = {
            'pick': pick['pick'],
            'team': pick['team_key'].split('.')[-1],
            'player': pick['player_key'].split('.')[-1]
        }
        results.append(result)
    except TypeError:
        pass


#
