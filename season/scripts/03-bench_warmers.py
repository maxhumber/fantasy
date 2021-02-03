from collections import Counter
import pandas as pd
pd.options.display.max_rows = 100

from utils import flatten, week, yahoo


# load
projections = pd.read_csv("season/data/weekly_projections.csv")


def fill_roster(input_df, date):
    df = input_df.copy().sort_values("ranking_custom")
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
    return roster

# # testing
# league, team = 84778, 12
# df = projections[projections["league"] == league]
# team = df[df["owner"] != "A"]
# fill_roster(team, "2021-02-04")


def simulate(input_df):
    df = input_df.copy()
    df["starts"] = 0
    dates = [
        date.strftime("%Y-%m-%d")
        for date in pd.to_datetime(df.columns, errors="coerce")
        if date >= pd.Timestamp("2020-01-01")
    ]
    for date in dates:
        roster = fill_roster(df, date)
        df.loc[df['name'].isin(flatten(roster)), "starts"] += 1
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

# # testing
# league, team = 84778, 12
# df = projections[projections["league"] == league]
# team = df[df["owner"] != "A"]
# simulate(team)


def drop_and_add(projections_df, drop_player, current_starts):
    df = projections_df.copy().sort_values("ranking_custom")
    df["starts_marginal"] = 0
    team = df[df["owner"] != "A"]
    team_after_drop = team[~team["name"].isin(drop_player)]
    available = df[df["owner"] == "A"].copy()
    for i, row in available.iterrows():
        possible_add = available.iloc[i:i+1]
        team_after_possible = pd.concat([team_after_drop, possible_add])
        roster_possible = simulate(team_after_possible)
        starts_marginal = roster_possible['starts'].sum() - current_starts
        available.loc[available['name'] == row["name"], "starts_marginal"] = starts_marginal
    df = available
    df = df[
        (df["starts_marginal"] >= 0) &
        (df["target"] == True)
    ]
    df = df[["name", "position", "ranking_custom", "starts_marginal"]]
    df = df.sort_values(["starts_marginal", "ranking_custom"], ascending=[False, True])
    return df

# # testing
# league, team = 84778, 12
# df = projections[projections["league"] == league]
# starts = 41
# drop = ["Nick Ritchie"]
# drop_and_add(df, drop, starts)


for league, team in yahoo.items():
    df = projections[projections["league"] == league]
    team = df[df["owner"] != "A"]
    roster = simulate(team)
    starts = roster['starts'].sum()
    drop = roster.tail(1)[["name"]]
    wire = drop_and_add(df, drop, starts)
    print(f"League: {league}\n")
    print(f"Roster:")
    print(roster)
    print("\n")
    print(f"Wire:")
    print(wire.head(10))
    print("\n")
