import pandas as pd
from gazpacho import Soup
import time
from tqdm import tqdm


def extract_lines(soup):
    lines = []
    for pos, n in [("f", 4), ("d", 3)]:
        for i in range(1, n + 1):
            players = soup.find("tr", {"id": f"{pos}{i}"})[0]
            line = [name.text for name in players.find("a")]
            for name in line:
                lines.append({"name": name, "line": i})
    return lines


def extract_ppu(soup):
    units = []
    for unit in [1, 2]:
        ppf = soup.find("table", {"summary": f"Powerplay 1 Forwards"})[unit - 1]
        players = ppf.find("span", {"class": "player-name"})
        names = [name.text for name in players]
        dl = (
            soup.find("td", {"id": f"PPLD{unit}"})
            .find("span", {"class": "player-name"})
            .text
        )
        dr = (
            soup.find("td", {"id": f"PPRD{unit}"})
            .find("span", {"class": "player-name"})
            .text
        )
        names.append(dl)
        names.append(dr)
        for name in names:
            units.append({"name": name, "ppu": unit})
    return units


def scrape(url):
    soup = Soup.get(url)
    lines = pd.DataFrame(extract_lines(soup))
    units = pd.DataFrame(extract_ppu(soup))
    df = pd.merge(lines, units, how="left", on="name")
    return df


soup = Soup.get("https://www.dailyfaceoff.com/teams/")
urls = [a.attrs["href"] for a in soup.find("a", {"class": "team-list-logo"})]

df = pd.DataFrame()
for url in tqdm(urls):
    di = scrape(url)
    df = df.append(di)
    time.sleep(0.5)

df.to_csv("data/lineups-dailyfaceoff_com.csv", index=False)
