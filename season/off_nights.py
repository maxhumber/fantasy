from gazpacho import Soup
import pandas as pd

date = "2021-01-25"

url = f"https://www.dailyfaceoff.com/nhl-weekly-schedule/{date.replace('-', '/')}"
soup = Soup.get(url)

table = soup.find("table", {"class": "weekly-schedule-table"})
th = table.find("tr", {"class": "weekly-schedule-head"}).find("th")
labels = [t.text for t in th]
trs = table.find("tr", {"class": "weekly-schedule-content-row"})

tr = trs[0]

def parse_tr(tr):
    values = [cell.text for cell in tr.find("td")]
    data = [[l, v] for l, v in zip(labels, values)]
    formatted = []
    for row in data[1:-1]:
        date = pd.Timestamp(f"{row[0]}, 2021").strftime("%Y-%m-%d")
        value = 1 if row[1] != "" else 0
        formatted.append([date, value])
    formatted.insert(0, data[0])
    return {k:v for k, v in formatted}

df = pd.DataFrame([parse_tr(tr) for tr in trs])
df = df.set_index("Team")
games = df.sum(axis=1)
off_day_score = (df / df.sum()).sum(axis=1)
df["games"] = games
df["off_day_score"] = off_day_score
df = df.sort_values(["games", "off_day_score"], ascending=[False, False])

df.head(5)
df.tail(10)




##
