import pandas as pd
from gazpacho import Soup

pd.options.display.max_rows = 500

def get_data(average=True, minimum_games=5, include_blocks=False):
    url = "https://www.hockey-reference.com/leagues/NHL_2021_skaters.html"
    df = pd.read_html(url)[0]
    df.columns = ['_'.join(col) for col in df.columns]
    df = df.rename(columns={
        'Unnamed: 1_level_0_Player': "player",
        'Unnamed: 3_level_0_Tm': "team",
        'Unnamed: 4_level_0_Pos': "position",
        'Unnamed: 5_level_0_GP': "GP",
        'Scoring_G': "G",
        'Scoring_A': "A",
        'Shot Data_S': "SOG",
        'Unnamed: 9_level_0_+/-': "+/-",
        'Unnamed: 23_level_0_BLK': "BLK",
        'Unnamed: 24_level_0_HIT': "HIT",
        'Special Teams_PP': "PPG",
        'Assists_PP': "PPA"
    })
    df = df[['player', 'team', 'position', 'GP', 'G', 'A', "+/-", "PPG", "PPA", "SOG", "HIT", "BLK"]]
    df = df.set_index(["player", "team", "position"])
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna()
    df = df[df["GP"] > minimum_games]
    df["PPP"] = df["PPG"] + df["PPA"]
    df = df[['GP', 'G', 'A', '+/-', 'PPP', 'SOG', 'HIT', "BLK"]]
    if not include_blocks:
        df = df.drop("BLK", axis=1)
    if average:
        df = df.apply(lambda x: round(x / x["GP"], 2), axis=1)
        df = df.drop("GP", axis=1)
    df = df.sort_values("G", ascending=False)
    return df

def rank(df):
    og = df.copy()
    df = df.copy().apply(lambda x: (x - x.mean()) / x.std())
    df["rank+"] = df[df.columns].median(axis=1)
    df["rank-"] = df[list(set(df.columns) - set(["+/-", "rank+"]))].median(axis=1)
    df["rank+"] = df["rank+"].rank(ascending=False)
    df["rank-"] = df["rank-"].rank(ascending=False)
    df["rankΔ"] = df["rank+"] - df["rank-"]
    df = df[["rank+", "rank-", "rankΔ"]]
    df = og.join(df)
    df = df.sort_values("rank+")
    df = df.reset_index()
    return df

df = get_data(include_blocks=False)
df = rank(df)

# yahoo
def name(tr):
    return tr.find("a", {"href": "/players/"}, mode="all")[-1].text

def players(league, team=None, position=None, count=0):
    team = team if team else "A"
    position = position if position else "P"
    url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/players"
    params = dict(
        status=team,
        pos=position,
        stat1="S_AS_2020",
        sort="AR",
        sdir=1,
        count=count,
    )
    soup = Soup.get(url, params)
    trs = soup.find("div", {"id": "players-table"}).find("tr")[2:]
    return [name(tr) for tr in trs]

# evaluation
league = 84778

team = df[df["player"].isin(players(league, 12))]

available = df[df["player"].isin(players(league))]
dmen = df[df["player"].isin(players(league, position="D"))]



#
