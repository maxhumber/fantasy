from collections import Counter
import pandas as pd
pd.options.display.max_rows = 100

from utils import flatten, week, yahoo


def fill_roster(df, date):
    slots_to_fill = Counter({'C': 2, 'LW': 2, 'RW': 2, 'D': 4})
    roster = {k: [] for k in slots_to_fill.keys()}
    for i, row in df.iterrows():
        if row[date] != 1:
            continue
        name = row["name"]
        positions = row['position'].split(",")
        for position in positions:
            if name not in flatten(roster):
                if slots_to_fill.get(position) > 0:
                    slots_to_fill[position] -= 1
                    roster.get(position).append(name)
    return roster, slots_to_fill


def simulate(df):
    df = df.copy()
    df["starts"] = 0
    dates = [
        date.strftime("%Y-%m-%d")
        for date in pd.to_datetime(df.columns, errors="coerce")
        if date >= pd.Timestamp("2020-01-01")
    ]
    for date in dates:
        roster, slots = fill_roster(df, date)
        df.loc[df['name'].isin(flatten(roster)), "starts"] += 1
    roster = df[["name", "position", "rank", "starts"]]
    roster = roster.sort_values(["starts", "rank"], ascending=[False, True])
    return roster


def drop_and_add(df, starts, drop):
    available = df[df["owner"] == "A"]
    team = df[df["owner"] != "A"]
    team_after_drop = team[~team["name"].isin(drop)]
    maybe = []
    for i, row in available.iterrows():
        possible_add = available.iloc[i:i+1]
        team_after_possible = pd.concat([team_after_drop, possible_add])
        roster_possible = simulate(team_after_possible)
        starts_possible = roster_possible['starts'].sum()
        starts_marginal = starts_possible - starts
        if starts_marginal > 0:
            maybe.append((row["name"], row["position"], row["rank"], starts_marginal))
    return maybe


projections = pd.read_csv("season/data/weekly_projections.csv")

for league, team in yahoo.items():
    df = projections[projections["league"] == league]
    team = df[df["owner"] != "A"]
    roster = simulate(team)
    starts = roster['starts'].sum()
    drop = roster.tail(1)[["name", "position", "rank"]]
    adds = drop_and_add(df, starts, drop)
    print(f"League: {league},\nDrop: {drop},\nAdd:\n", adds)
    print("\n")
