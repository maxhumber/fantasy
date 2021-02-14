import time
import random
import pandas as pd
from gazpacho import Soup
from tqdm import tqdm

from season.schedule import schedule
from utils import team_codes


def possible_teams():
    df = schedule()
    df = df.rename(columns={"home": "team"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["team", "date"])
    df["shift"] = df.groupby("team")["date"].shift(1)
    df["back_to_back"] = (df["date"] - df["shift"]).dt.days <= 1
    games = df.groupby("team")[["away_record"]].count()
    games = games.rename(columns={"away_record": "games"})
    opponents = df.groupby("team")[["away_record"]].mean().reset_index()
    opponents = opponents.rename(columns={"away_record": "opponent_record"})
    back_to_back = df.groupby("team")[["back_to_back"]].sum().reset_index()
    df = pd.merge(games, opponents, how="left", on="team")
    df = pd.merge(df, back_to_back, how="left", on="team")
    df = df[
        (df["back_to_back"] == 1) &
        (df["opponent_record"] <= 0.5)
    ]
    df = df.sort_values("opponent_record")
    df["team"] = df["team"].replace({v: k for k, v in team_codes.items()})
    return df

def parse_td(td):
    name = td.find("a").text
    try:
        rating = td.find("span", {"class": "rating-rank"}).text
        rating = rating.replace("#", "")
        rank, depth = rating.split(" G")
    except:
        rank, depth = None, None
    return dict(name=name, rank=rank, depth=depth)

def scrape_depth(team):
    soup = Soup.get(f"https://www.dailyfaceoff.com/teams/{team}/line-combinations/")
    tr = soup.find("tr", {"id": "g"})
    return [parse_td(td) for td in tr.find("td")]

def possible():
    df = possible_teams()
    goalies = []
    for i, row in tqdm(df.iterrows()):
        g = scrape_depth(row["team"])
        goalies.extend(g)
        time.sleep(random.uniform(5, 30) / 10)
    goalies = pd.DataFrame(goalies)
    return goalies

def parse_tr(tr):
    name = tr.find("a", {"href": "players"})[-1].text
    team = tr.find("span", {"class": "Fz-xxs"})[0].text.split(" - ")[0]
    return dict(name=name, team=team)

def available(league):
    url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/players"
    params = dict(sort="AR", sdir=1, status="A", pos="G", stat1="S_S_2020")
    soup = Soup.get(url, params)
    table = soup.find("div", {"id": "players-table"}, mode="first")
    trs = table.find("tr")[2:]
    df = pd.DataFrame([parse_tr(tr) for tr in trs])
    return df
