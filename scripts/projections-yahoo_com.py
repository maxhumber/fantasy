import time
from itertools import chain

from gazpacho import Soup
import pandas as pd

def parse_skater(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    stats = tr.find("td", {"class": "Ta-end"})[3:]
    stats = [float(s.text) for s in stats]
    labels = ["goals", "assists", "plus_minus", "powerplay_points", "shots_on_goal", "hits"]
    data = dict(zip(labels, stats))
    data["name"] = name
    return data

def parse_goalie(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    stats = tr.find("td", {"class": "Ta-end"})[3:]
    stats = [float(s.text) for s in stats]
    labels = ["wins", "goals_against", "goals_against_average", "saves", "shots_against", "save_percentage", "shutouts"]
    data = dict(zip(labels, stats))
    data["name"] = name
    return data

def scrape(parse, position, offset=0):
    url = "https://hockey.fantasysports.yahoo.com/hockey/84570/players"
    params = dict(
        status="A",
        pos=position,
        cut_type=33,
        stat1="S_PSR",
        myteam=0,
        sort="OR",
        sdir=1,
        count=offset
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    data = [parse(tr) for tr in trs]
    time.sleep(0.5)
    return data

skaters = [scrape(parse_skater, "P", offset) for offset in range(0, 300, 25)]
sdf = pd.DataFrame(list(chain(*skaters)))

goalies = [scrape(parse_goalie, "G", offset) for offset in range(0, 50+25, 25)]
gdf = pd.DataFrame(list(chain(*goalies)))

df = pd.concat([sdf, gdf])
df["source"] = "Yahoo"
df["fetched_at"] = pd.Timestamp("now")
df["blocks"] = None
df["team"] = None
df["position"] = None

df = df[
    [
        "source",
        "fetched_at",
        "team",
        "position",
        "name",
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
