import time
import random
from gazpacho import Soup
import pandas as pd
from tqdm import tqdm

from utils import yahoo


def get_matchup(week, team, league):
    url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/matchup"
    params = dict(week=week, module="matchup", mid1=team)
    soup = Soup.get(url, params)
    teams = soup.find("a", {"class": "F-link"})[:2]
    teams = [int(t.attrs["href"].split("/")[-1]) for t in teams]
    home, away = teams
    date = (
        soup.find("a", {"href": "week="})[3].attrs["href"].split("&")[1].split("=")[-1]
    )
    return dict(league=league, week=week, date=date, home=home, away=away)


if __name__ == "__main__":
    matchups = []
    for league, team in tqdm(yahoo.items()):
        for week in range(2, 13 + 1):
            matchup = get_matchup(week, team, league)
            matchups.append(matchup)
            time.sleep(random.uniform(1, 10) / 5)
    df = pd.DataFrame(matchups)
    df.to_csv("season/data/weekly_fantasy_matchups.csv", index=False)
