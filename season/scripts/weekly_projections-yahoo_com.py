import time
from itertools import chain
from gazpacho import Soup
import pandas as pd


def get_trs(team, league, position="P"):
    url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/players"
    params = dict(
        sort="AR",
        sdir=1,
        status=team,
        pos=position,
        stat1="S_PS7"
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    return trs

def parse_skater_tr(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    owner = int(tr.find("a", {"href": "hockey"}).attrs["href"].split("/")[-1])
    data = [td.text for td in tr.find("td")][5:-1]
    data = [pd.to_numeric(d.replace("%", ""), errors="coerce") for d in data]
    labels = ["gp", "ranking_preseason", "ranking_current", "rostered", "goals", "assists", "plus_minus", "powerplay_points", "shots_on_goal", "hits"]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(" - ")
    player = dict(zip(labels, data))
    player["name"] = name
    player["team"] = team
    player["position"] = position
    player["owner"] = owner
    return player

def parse_goalie_tr(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    owner = int(tr.find("a", {"href": "hockey"}).attrs["href"].split("/")[-1])
    data = [td.text for td in tr.find("td")][5:-1]
    data = [pd.to_numeric(d.replace("%", ""), errors="coerce") for d in data]
    labels = ["gp", "ranking_preseason", "ranking_current", "rostered", "wins", "goals_against", "goals_against_average", "saves", "shots_against", "save_percentage", "shutouts"]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(" - ")
    player = dict(zip(labels, data))
    player["name"] = name
    player["team"] = team
    player["position"] = position
    player["owner"] = owner
    return player

def get_projections(team, league):
    trs = get_trs(team, league, position="P")
    skaters = [parse_skater_tr(tr) for tr in trs]
    time.sleep(0.1)
    trs = get_trs(team, league, position="G")
    goalies = [parse_goalie_tr(tr) for tr in trs]
    df = pd.concat([pd.DataFrame(skaters), pd.DataFrame(goalies)])
    df = df[[
        'owner', 'name', 'team', 'position',
        'goals', 'assists', 'plus_minus', 'powerplay_points', 'shots_on_goal', 'hits',
        'wins', 'saves', 'shots_against', 'shutouts'
    ]]
    return df

def get_matchup_projections(home, away, league):
    hdf = get_projections(home, league)
    time.sleep(0.5)
    adf = get_projections(away, league)
    hdf["owner"] = f"Me ({home})"
    adf["owner"] = f"Opponent ({away})"
    df = pd.concat([hdf, adf])
    df = df.groupby("owner").sum()
    df["save_percentage"] = df["saves"] / df["shots_against"]
    df = df[[
        'goals', 'assists', 'plus_minus', 'powerplay_points',
        'shots_on_goal', 'hits', 'wins', 'save_percentage', 'shutouts'
    ]].T.round(3)
    return df

matchups = pd.read_csv("data/matchups_list-yahoo_com.csv")
week = 2
week_matchups = matchups[matchups["week"] == week].copy()

for i, row in week_matchups.iterrows():
    print(row.league)
    print(get_matchup_projections(row.home, row.away, row.league))
    print("\n")



#
