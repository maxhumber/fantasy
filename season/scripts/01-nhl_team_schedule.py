# https://www.dailyfaceoff.com/nhl-weekly-schedule

from gazpacho import Soup
import pandas as pd

from utils import team_codes, monday, next_monday


def get_trs(date):
    url = f"https://www.dailyfaceoff.com/nhl-weekly-schedule/{date.replace('-', '/')}"
    soup = Soup.get(url)
    table = soup.find("table", {"class": "weekly-schedule-table"})
    th = table.find("tr", {"class": "weekly-schedule-head"}).find("th")
    labels = [t.text for t in th]
    trs = table.find("tr", {"class": "weekly-schedule-content-row"})
    return trs, labels


def parse_tr(tr, labels):
    team = tr.find("a", {"class": "team-logo"}, mode="first").attrs["href"].split("/")[-3]
    values = [cell.text for cell in tr.find("td")]
    values[0] = team
    data = [[l, v] for l, v in zip(labels, values)]
    formatted = []
    for row in data[1:-1]:
        date = pd.Timestamp(f"{row[0]}, 2021").strftime("%Y-%m-%d")
        value = 1 if row[1] != "" else 0
        formatted.append([date, value])
    formatted.insert(0, data[0])
    return {k:v for k, v in formatted}


def fetch_schedule(date):
    trs, labels = get_trs(date)
    df = pd.DataFrame([parse_tr(tr, labels) for tr in trs])
    df = df.rename(columns={"Team": "team"})
    return df


def calculate_off_days(df):
    df = df.set_index("team")
    games = df.sum(axis=1)
    off_day_score = round((df / df.sum()).sum(axis=1), 2)
    df["games"] = games
    df["off_day_score"] = off_day_score
    df = df.sort_values(["off_day_score", "games"], ascending=[False, False])
    return df


def scrape(monday, next_monday):
    week_1 = fetch_schedule(monday)
    week_2 = fetch_schedule(next_monday)
    df = pd.merge(week_1, week_2)
    df = df.melt(id_vars="team", var_name="date", value_name="plays")
    df['date'] = pd.to_datetime(df["date"])
    df = df[
        (df['date'] >= pd.Timestamp("today").normalize()) &
        (df['date'] < (pd.Timestamp("today") + pd.Timedelta("6 days")))
    ]
    df['date'] = df['date'].dt.strftime("%Y-%m-%d")
    df['team'] = df['team'].replace(team_codes)
    df = df.pivot(index="team", columns="date", values="plays")
    df = df.reset_index()
    df = calculate_off_days(df)
    return df


if __name__ == "__main__":
    df = scrape(monday, next_monday)
    df.to_csv("season/data/nhl_team_schedule.csv")
