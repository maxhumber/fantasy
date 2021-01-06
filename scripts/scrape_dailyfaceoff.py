import pandas as pd
from gazpacho import Soup, get

url = "https://www.dailyfaceoff.com/fantasy-hockey-projections/"
html = get(url)
soup = Soup(html)
skaters, goalies = soup.find("table", {"id": "igsv"})
sdf = pd.read_html(str(skaters))[0]
gdf = pd.read_html(str(goalies))[0]
df = pd.concat([sdf, gdf]).reset_index(drop=True)

column_mappings = {
    "Players": "name",
    "TEAM": "team",
    "POS.": "position",
    "G": "goals",
    "A": "assists",
    "(+/-)": "plus_minus",
    "PPP": "powerplay_points",
    "SOG": "shots_on_goal",
    "HIT": "hits",
    "BLK": "blocks",
    "W": "wins",
    "GAA": "goals_against_average",
    "save_percentage": "SV%",
    "SV": "saves",
    "SO": "shutouts",
}


df = df.rename(columns=column_mappings)
df["save_percentage"] = df["SV%"]
df["source"] = "Daily Faceoff"
df["fetched_at"] = pd.Timestamp("now")

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

df.to_csv("data/dailyfaceoff.csv", index=False)
