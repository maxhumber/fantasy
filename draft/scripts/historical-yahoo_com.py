import time
from itertools import chain, product

from gazpacho import Soup
import pandas as pd
from tqdm import tqdm


def parse_skater(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    data = [td.text for td in tr.find("td")][5:-1]
    data = [
        pd.to_numeric(d.replace("%", "").replace(":", "."), errors="coerce")
        for d in data
    ]
    labels = [
        "gp",
        "ranking_preseason",
        "ranking_current",
        "rostered",
        "toi",
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
    data = [
        pd.to_numeric(d.replace("%", "").replace(":", "."), errors="coerce")
        for d in data
    ]
    labels = [
        "gp",
        "ranking_preseason",
        "ranking_current",
        "rostered",
        "toi",
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


def scrape(parse, position, year, offset=0):
    url = "https://hockey.fantasysports.yahoo.com/hockey/84570/players"
    params = dict(
        status="ALL",
        pos=position,
        cut_type=33,
        stat1=f"S_S_{year}",
        myteam=0,
        sort="AR",
        sdir=1,
        count=offset,
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    data = [parse(tr) for tr in trs]
    return data


variables = list(product(["P", "G"], [2018, 2019], range(0, 300, 25)))

df = pd.DataFrame()
for position, year, offset in tqdm(variables):
    if position == "G":
        parse = parse_goalie
    else:
        parse = parse_skater
    if position == "G" and offset > 50:
        continue
    di = pd.DataFrame(scrape(parse, position, year, offset))
    di["year"] = year
    df = df.append(di)
    time.sleep(0.5)

df["source"] = "Yahoo"
df["fetched_at"] = pd.Timestamp("now")
df["blocks"] = None

df = df[
    [
        "source",
        "fetched_at",
        "year",
        "team",
        "position",
        "name",
        "gp",
        "toi",
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

df.to_csv("data/historical-yahoo_com.csv", index=False)
