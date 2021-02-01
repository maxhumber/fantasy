from collections import Counter
import pandas as pd


def flatten(d):
    return [item for sublist in d.values() for item in sublist]


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


def simulate(week, league, team):
    projections = pd.read_csv(f"season/data/weekly_projections_{week}_{league}_{team}.csv")
    df = pd.merge(
        projections,
        schedule.drop(["games", "off_day_score"], axis=1),
        how="left",
        on="team"
    ).sort_values("rank")
    df['rostered'] = 0
    sdf = pd.DataFrame()
    for date in dates:
        roster, slots = fill_roster(df, date)
        names = flatten(roster)
        df.loc[df['name'].isin(names), "rostered"] += 1
        idf = pd.DataFrame(slots, index=[date])
        sdf = sdf.append(idf)
    slots = sdf
    rostered = df[["name", "position", "rank", "rostered"]]
    return slots, rostered


if __name__ == "__main__":
    week = 3
    matchups = pd.read_csv("season/data/weekly_fantasy_matchups.csv")
    mw = matchups[matchups["week"] == week]

    schedule = pd.read_csv("season/data/nhl_team_schedule.csv")
    schedule["team"] = schedule["team"].replace(team_codes)
    dates = schedule.drop(["team", "games", "off_day_score"], axis=1).columns.tolist()

    for i, row in mw.iterrows():
        league, week, date, home, away = row
        print(f"{week} - {league} - {home}")
        slots, rostered = simulate(week, league, home)
        print(f"OPEN SLOTS:")
        print(slots)
        print("ACTIVE ROSTER:")
        print(rostered)
        print("\n")

    schedule[
        (schedule["2021-02-02"] == 0) &
        (schedule["2021-02-04"] == 0)
    ]




    #
