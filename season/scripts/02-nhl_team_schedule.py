from gazpacho import Soup
import pandas as pd
import datetime

def get_trs(date):
    url = "https://www.dailyfaceoff.com/nhl-weekly-schedule/"
    # url = f"https://www.dailyfaceoff.com/nhl-weekly-schedule/{date.replace('-', '/')}"
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
    df = df.sort_values(["games", "off_day_score"], ascending=[False, False])
    return df


def scrape(date):
    df = fetch_schedule(date)
    df = calculate_off_days(df)
    return df


if __name__ == "__main__":
    today = datetime.date.today()
    date = today + datetime.timedelta(days=-today.weekday())
    date = date.strftime("%Y-%m-%d")
    df = scrape(date)
    df.to_csv("season/data/nhl_team_schedule.csv")
