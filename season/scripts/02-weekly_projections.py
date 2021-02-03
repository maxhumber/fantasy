import time
import random
from itertools import chain
from gazpacho import Soup
import pandas as pd
import numpy as np

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

from utils import yahoo


schedule = pd.read_csv("season/data/nhl_team_schedule.csv")


def parse(tr):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    values = [td.text for td in tr.find("td")][5:-1]
    values = [pd.to_numeric(v.replace("%", ""), errors="coerce") for v in values]
    labels = ["gp", "ranking_draft", "ranking_current", "rostered", "goals", "assists", "plus_minus", "powerplay_points", "shots_on_goal", "hits"]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(" - ")
    data = dict(zip(labels, values))
    player = dict(name=name, team=team, position=position)
    return {**player, **data}


def scrape_page(league, team, count=0, position="P"):
    url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/players"
    params = dict(
        sort="AR",
        sdir=1,
        status=team,
        pos=position,
        stat1="S_PS7",
        count=count
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    df = pd.DataFrame([parse(tr) for tr in trs])
    df["league"] = league
    df["owner"] = team
    return df


def scrape_league(league, team):
    df = pd.DataFrame()
    for team, count in [(team, 0), ("A", 0), ("A", 25), ("A", 50)]:
        dp = scrape_page(league, team, count)
        df = df.append(dp)
        time.sleep(random.uniform(1, 10) / 10)
    df = df.drop(["gp", "ranking_current", "rostered"], axis=1).reset_index()
    return df


def custom_rank(df):
    dr = df[['name', 'goals', 'assists', 'powerplay_points', 'shots_on_goal', 'hits']]
    dr = dr.set_index("name")
    dr = dr.apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    dr["rollup"] = dr.apply(lambda row: row.sum(), axis=1)
    dr["ranking_custom"] = dr["rollup"].rank(ascending=False)
    dr["target"] = ((dr["powerplay_points"] >= 0.20) & (dr["hits"] >= 0.20))
    dr = dr.reset_index()[["name", "ranking_custom", "target"]]
    df = pd.merge(df, dr, on="name", how="left")
    df = df[[
        'league', 'owner', 'name', 'team', 'position',
        'ranking_draft', 'ranking_custom', 'target',
        'goals', 'assists', 'plus_minus', 'powerplay_points', 'shots_on_goal', 'hits'
    ]]
    df = df.sort_values("ranking_custom")
    return df


if __name__ == "__main__":
    df = pd.DataFrame()
    for league, team in yahoo.items():
        dl = scrape_league(league, team)
        dr = custom_rank(dl)
        df = df.append(dr)
    df = pd.merge(df, schedule, how="left", on="team")
    df['fetched'] = pd.Timestamp("now")
    df.to_csv("season/data/weekly_projections.csv", index=False)
