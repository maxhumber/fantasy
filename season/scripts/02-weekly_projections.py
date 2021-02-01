import time
import random
from itertools import chain
from gazpacho import Soup
import pandas as pd

from utils import week, yahoo


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


def scrape(league, team, count=0, position="P"):
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
    skaters = pd.DataFrame([parse(tr) for tr in trs])
    skaters["league"] = league
    skaters["owner"] = team
    return skaters


def get_projections(week, yahoo):
    df = pd.DataFrame()
    for league, team in yahoo.items():
        for team, count in [(team, 0), ("A", 0), ("A", 25)]:
            skaters = scrape(league, team, count)
            df = df.append(skaters)
            time.sleep(random.uniform(1, 10) / 10)
    df = pd.merge(df, schedule, how="left", on="team")
    multiplier_current = (week / 13) # 13 total weeks
    multiplier_draft = 1 - multiplier_current
    df["ranking_draft"] *= multiplier_draft
    df["ranking_current"] *= multiplier_current
    df["rank"] = round((df["ranking_draft"] + df["ranking_current"]) / 2, 1)
    df = df.sort_values("rank")
    return df


if __name__ == "__main__":
    df = get_projections(week, yahoo)
    df['fetched'] = pd.Timestamp("now")
    df.to_csv("season/data/weekly_projections.csv", index=False)
