import pandas as pd
from collections import Counter
from team_codes import team_codes

# standard slots
SLOTS = Counter({'C': 2, 'LW': 2, 'RW': 2, 'D': 4})

# schedule data
schedule = pd.read_csv("season/data/nhl_team_schedule.csv")
schedule["team"] = schedule["team"].replace(team_codes)
dates = schedule.drop(["team", "games", "off_day_score"], axis=1).columns.tolist()

# functions
def fill_roster(df, date):
    # fill this shit
    slots_to_fill = SLOTS.copy()
    roster = []

    for i, row in df.iterrows():
        # if not playing skip...
        if row[date] != 1:
            continue

        name = row["name"]
        positions = row['position'].split(",")

        for position in positions:
            # check if name isn't added
            if name not in roster:
                if slots_to_fill.get(position) > 0:
                    slots_to_fill[position] -= 1
                    roster.append(row["name"])
    return roster

def check_bench(df, date, roster):
    bdf = df[
        (~df["name"].isin(roster)) &
        (df[date] == 1)
    ]
    return bdf["name"].tolist()

# week = 2
# league = 84570
# team = 3
# date = dates[1]

def low_utilization(week, league, team):
    projections = pd.read_csv(f"season/data/weekly_projections_{week}_{league}_{team}.csv")

    df = pd.merge(
        projections,
        schedule.drop(["games", "off_day_score"], axis=1),
        how="left",
        on="team"
    ).sort_values("rank")

    df['rostered'] = 0
    for date in dates:
        rostered = fill_roster(df, date)
        df.loc[df['name'].isin(rostered), "rostered"] += 1

    df = (
        df[
            (df["rank"] >= 50) &
            (df["rostered"] <= 2)
        ]
        [["name", "position", 'team', 'rank', 'rostered']]
    )

    return df


if __name__ == "__main__":
    # matchup data
    week = 2
    matchups = pd.read_csv("season/data/weekly_fantasy_matchups.csv")
    mw = matchups[matchups["week"] == week]

    # go through all of them
    for i, row in mw.iterrows():
        league, week, date, home, away = row
        print(f"{week} - {league} - {home}")
        print(low_utilization(week, league, home))

    print("\nTarget streamers from these teams:")
    print(
        schedule
        .sort_values("off_day_score", ascending=False)
        [['team', 'games', 'off_day_score']]
        .head(5)
    )
