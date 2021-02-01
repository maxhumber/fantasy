import time
from itertools import chain
from gazpacho import Soup
import pandas as pd

from utils import week


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
    try:
        owner = int(tr.find("a", {"href": "hockey"}).attrs["href"].split("/")[-1])
    except:
        owner = None
    values = [td.text for td in tr.find("td")][5:-1]
    values = [pd.to_numeric(v.replace("%", ""), errors="coerce") for v in values]
    labels = ["gp", "ranking_draft", "ranking_current", "rostered", "goals", "assists", "plus_minus", "powerplay_points", "shots_on_goal", "hits"]
    team, position = tr.find("span", {"class": "Fz-xxs"}, mode="first").text.split(" - ")
    data = dict(zip(labels, values))
    player = dict(name=name, team=team, position=position)
    return {**player, **data}


def scrape(week, team, league):
    trs = get_trs(team, league, position="P")
    df = pd.DataFrame([parse_skater_tr(tr) for tr in trs])
    multiplier_current = (week / 13) # 13 total weeks
    multiplier_draft = 1 - multiplier_current
    df["ranking_draft"] *= multiplier_draft
    df["ranking_current"] *= multiplier_current
    df["rank"] = round((df["ranking_draft"] + df["ranking_current"]) / 2, 1)
    df = df.sort_values("rank")
    df = df.drop(["gp", "rostered", "ranking_draft", "ranking_current"], axis=1)
    return df


if __name__ == "__main__":
    current_week = week()
    matchups = pd.read_csv("season/data/weekly_fantasy_matchups.csv")
    mw = matchups[matchups["week"] == current_week]
    for i, row in mw.iterrows():
        # my players
        df = scrape(row.week, row.home, row.league)
        df.to_csv(f"season/data/weekly_projections_{row.week}_{row.league}_{row.home}.csv", index=False)
        time.sleep(0.5)
        # available
        df = scrape(current_week, "A", row.league)
        df.to_csv(f"season/data/weekly_projections_{row.week}_{row.league}_available.csv", index=False)
        time.sleep(0.5)
