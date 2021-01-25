import pandas as pd
from gazpacho import Soup
import numpy as np
pd.options.display.max_columns = 100

# dates
start = "2021-01-25"
start = pd.Timestamp(start)
end = start + pd.Timedelta("6 days")

# parameters
league = 84778
team = 12
position = "P"

# get data
url = f"https://hockey.fantasysports.yahoo.com/hockey/{league}/players"
params = dict(
    sort="AR",
    sdir=1,
    status=team,
    pos=position,
    stat1="O_O"
)

soup = Soup.get(url, params)
table = soup.find("div", {"id": "players-table"})
labels = [th.text for th in table.find("tr")[1].find("th")]
trs = table.find("tr")[2:]

# to test
tr = trs[0]

def parse_tr(tr, labels):
    name = tr.find("a", {"href": "players"}, mode="list")[-1].text
    about = tr.find("span", {"class": "Fz-xxs"}, partial=False).text
    team, position = about.split(" - ")
    values = [td.text for td in tr.find("td")]
    predraft, current = values[5:6+1]
    data = list(zip(labels, values))
    date_data = data[8:-1]
    # filter date_data
    filtered = []
    for row in date_data:
        date = pd.Timestamp(f"{row[0]}/21")
        value = 1 if row[1] != "" else 0
        if start <= date <= end:
            date = date.strftime("%Y-%m-%d")
            filtered.append((date, value))
    dates = {k: v for k, v in filtered}
    player = dict(
        name=name,
        position=position,
        predraft=int(predraft),
        current=int(current)
    )
    return {**player, **dates}

# dataframe-ize
df = pd.DataFrame([parse_tr(tr, labels) for tr in trs])

df[df["position"].str.contains("D")]



#
