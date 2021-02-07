from collections import Counter
import pandas as pd
pd.options.display.max_rows = 100

from utils import flatten, week, yahoo


# load projections
projections = pd.read_csv("season/data/weekly_projections.csv")


# extract dates
def extract_dates(df):
    dates = [
        date.strftime("%Y-%m-%d")
        for date in pd.to_datetime(df.columns, errors="coerce")
        if date >= pd.Timestamp("2020-01-01")
    ]
    return dates


# fill for one date
def fill(df):
    slots = Counter({'C': 2, 'LW': 2, 'RW': 2, 'D': 4})
    roster = {k: [] for k in slots.keys()}
    for i, row in df.iterrows():
        name = row["name"]
        positions = row['position'].split(",")
        for position in positions:
            if name not in flatten(roster):
                if slots.get(position) > 0:
                    slots[position] -= 1
                    roster.get(position).append(name)
    return roster


# fill for league for all dates
def fill_all_for(projections, league, drop=[], add=[]):
    df = projections.copy()
    df = df[df["league"] == league]
    team = (df["owner"] != "A") & (~df["name"].isin(drop))
    maybe = df["name"].isin(add)
    df = df[team | maybe]
    df["starts"] = 0
    for date in extract_dates(df):
        roster = fill(df[df[date] == 1])
        df.loc[df['name'].isin(flatten(roster)), "starts"] += 1
    roster = df
    return roster


# score the filled out roster
def score(roster):
    df = roster.copy()
    df["keeper"] = (
        df["ranking_draft"].rank() +
        df["ranking_custom"].rank() +
        df["starts"].rank(ascending=False)
    )
    df["keeper"] = df[["keeper"]].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    df = df.sort_values("keeper")
    df["keeper"] = 1 - df["keeper"]
    df = df[["name", "position", "ranking_draft", "ranking_custom", "starts", "keeper"]]
    return df


# combine both
def fill_and_score(projections, league, drop=[], add=[]):
    roster = fill_all_for(projections, league, drop, add)
    df = score(roster)
    return df


# look for pickup
def drop_and_add(projections, league, drop, starts):
    df = projections.copy()
    df = df[(df["league"] == league) & (df["owner"] == "A")]
    df = df.reset_index(drop=True)
    df["starts_marginal"] = 0
    for i, row in df.iterrows():
        add = row["name"]
        maybe = fill_and_score(projections, league, drop, [add])
        df.loc[df['name'] == add, "starts_marginal"] = maybe["starts"].sum() - starts
    # df = df[
    #     (df["starts_marginal"] >= 0) &
    #     (df["target"] == True)
    # ]
    df = df[["name", "position", "ranking_custom", "starts_marginal"]]
    df = df.sort_values(["starts_marginal", "ranking_custom"], ascending=[False, True])
    return df


# look for stuff
league = 84919
roster = fill_and_score(projections, league)
starts = roster["starts"].sum()

roster

drop = ["Chris Kreider"]

drop_and_add(projections, league, drop, starts)





#
