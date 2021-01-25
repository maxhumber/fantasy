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
    values = [td.text for td in tr.find("td")][5:-1]
    values = [pd.to_numeric(v.replace("%", ""), errors="coerce") for v in values]
    labels = ["gp", "ranking_draft", "ranking_current", "rostered", "goals", "assists", "plus_minus", "powerplay_points", "shots_on_goal", "hits"]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(" - ")
    data = dict(zip(labels, values))
    player = dict(name=name, team=team, position=position)
    return {**player, **data}

# get data
team = 12
league = 84778
trs = get_trs(team, league, position="P")

# dataframe
df = pd.DataFrame([parse_skater_tr(tr) for tr in trs])

# correct rankings
week = 2
multiplier_current = (week / 13)
multiplier_draft = 1 - multiplier_current
df["ranking_draft"] *= multiplier_draft
df["ranking_current"] *= multiplier_current
df["rank"] = round((df["ranking_draft"] + df["ranking_current"]) / 2, 1)
df = df.sort_values("rank")

# drop
df = df.drop(["gp", "rostered", "ranking_draft", "ranking_current"], axis=1)

df

















#
