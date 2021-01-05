import time
from itertools import chain

import pandas as pd
from gazpacho import Soup


def scrape(offset=0):
    url = f"https://hockey.fantasysports.yahoo.com/hockey/draftanalysis?tab=SD&pos=ALL&sort=DA_AP&count={offset}"
    soup = Soup.get(url)
    table = soup.find("table", {"id": "draftanalysistable"})
    trs = table.find("tr")[1:]
    data = []
    for tr in trs:
        name = tr.find("a", {"class": "name"}).text
        pick = float(tr.find("td", {"class": "Ta-end"}).text)
        info = tr.find("span", {"class": "Fz-xxs"}, mode="first").text
        team, position = info.split(" - ")
        data.append({"name": name, "team": team, "position": position, "pick": pick})
    time.sleep(0.5)
    return data


data = [scrape(offset) for offset in range(0, 300, 50)]

pd.DataFrame(list(chain(*data))).to_csv("data/yahoo.csv", index=False)
