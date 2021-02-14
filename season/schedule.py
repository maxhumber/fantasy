from gazpacho import Soup
import pandas as pd

from utils import team_codes, monday, next_monday


def scrape(date):
    """https://www.dailyfaceoff.com/nhl-weekly-schedule"""
    url = f"https://www.dailyfaceoff.com/nhl-weekly-schedule/{date.replace('-', '/')}"
    soup = Soup.get(url)
    table = soup.find("table", {"class": "weekly-schedule-table"})
    th = table.find("tr", {"class": "weekly-schedule-head"}).find("th")
    ths = [t.text for t in th]
    trs = table.find("tr", {"class": "weekly-schedule-content-row"})
    return ths, trs


def extract(th, td):
    try:
        team = td.find("a", {"class": "team-logo"}).attrs["href"].split("/")[-3]
        record = (
            td.find("span", {"class": "team-record"})
            .text.replace("(", "")
            .replace(")", "")
        )
    except AttributeError:
        team, record = None, None
    return dict(date=th, away=team, away_record=record)


def parse(ths, tr):
    tds = tr.find("td")
    zipped = zip(ths, tds)
    row = [extract(th, td) for th, td in zipped]
    home = row[0]["away"]
    home_record = row[0]["away_record"]
    week = row[1:-1]
    for day in week:
        day["home"] = home
        day["home_record"] = home_record
    return week


def frame(date):
    ths, trs = scrape(date)
    data = []
    for tr in trs:
        row = parse(ths, tr)
        data.extend(row)
    df = pd.DataFrame(data)
    df["date"] = df["date"].apply(lambda x: pd.Timestamp(f"{x}, 2021"))
    df["home"] = df["home"].replace(team_codes)
    df["away"] = df["away"].replace(team_codes)
    df = df.dropna(subset=["away"]).reset_index(drop=True)
    df = df[["date", "home", "away", "away_record"]]
    return df


def fetch_schedule(monday, next_monday):
    week_1 = frame(monday)
    week_2 = frame(next_monday)
    df = pd.concat([week_1, week_2])
    return df


def percentize(record):
    w, l, t = record.split("-")
    w, l, t = int(w), int(l), int(t)
    return w / (w + l + t)


def calculate_off_days(df):
    df = df.set_index("team")
    games = df.sum(axis=1)
    off_day_score = round((df / df.sum()).sum(axis=1), 2)
    df["games"] = games
    df["off_day_score"] = off_day_score
    df = df.sort_values(["off_day_score", "games"], ascending=[False, False])
    return df


def schedule():
    df = fetch_schedule(monday, next_monday)
    df["away_record"] = df["away_record"].apply(lambda x: percentize(x))
    df = df[
        (df["date"] > pd.Timestamp("today").normalize())
        & (df["date"] < (pd.Timestamp("today") + pd.Timedelta("7 days")))
    ]
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df["fetched_at"] = pd.Timestamp("now")
    return df


def pivot_schedule():
    df = schedule()
    df["plays"] = 1
    df = df.pivot(index="home", columns="date", values="plays")
    df = df.reset_index()
    df = df.rename(columns={"home": "team"})
    df = df.fillna(0)
    df = calculate_off_days(df)
    df = df.reset_index()
    return df
