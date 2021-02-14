import time
from itertools import chain

from gazpacho import Soup
import pandas as pd


def parse_skater(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    data = [td.text for td in tr.find("td")][5:-1]
    data = [float(d.replace("%", "")) for d in data]
    labels = [
        "gp",
        "ranking_preseason",
        "ranking_current",
        "rostered",
        "goals",
        "assists",
        "plus_minus",
        "powerplay_points",
        "shots_on_goal",
        "hits",
    ]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(
        " - "
    )
    player = dict(zip(labels, data))
    player["name"] = name
    player["team"] = team
    player["position"] = position
    return player


def parse_goalie(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    data = [td.text for td in tr.find("td")][5:-1]
    data = [float(d.replace("%", "")) for d in data]
    labels = [
        "gp",
        "ranking_preseason",
        "ranking_current",
        "rostered",
        "wins",
        "goals_against",
        "goals_against_average",
        "saves",
        "shots_against",
        "save_percentage",
        "shutouts",
    ]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(
        " - "
    )
    player = dict(zip(labels, data))
    player["name"] = name
    player["team"] = team
    player["position"] = position
    return player


def scrape(parse, position, offset=0):
    url = "https://hockey.fantasysports.yahoo.com/hockey/84570/players"
    params = dict(
        status="A",
        pos=position,
        cut_type=33,
        stat1="S_PSR",
        myteam=0,
        sort="AR",
        sdir=1,
        count=offset,
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    data = [parse(tr) for tr in trs]
    time.sleep(0.5)
    return data


skaters = [scrape(parse_skater, "P", offset) for offset in range(0, 300, 25)]
sdf = pd.DataFrame(list(chain(*skaters)))

goalies = [scrape(parse_goalie, "G", offset) for offset in range(0, 50 + 25, 25)]
gdf = pd.DataFrame(list(chain(*goalies)))

df = pd.concat([sdf, gdf])
df["source"] = "Yahoo"
df["fetched_at"] = pd.Timestamp("now")
df["blocks"] = None

df = df[
    [
        "source",
        "fetched_at",
        "team",
        "position",
        "name",
        "ranking_preseason",
        "ranking_current",
        "goals",
        "assists",
        "plus_minus",
        "powerplay_points",
        "shots_on_goal",
        "hits",
        "blocks",
        "wins",
        "saves",
        "save_percentage",
        "goals_against_average",
        "shutouts",
    ]
]

df.to_csv("data/projections-yahoo_com.csv", index=False)
