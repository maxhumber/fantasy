import re
import time

import pandas as pd
from gazpacho import Soup, get

df = pd.DataFrame()

for page in range(1, 10 + 1):
    url = f"https://www.capfriendly.com/browse/active/2021/salary?age-calculation-date=today&hide=team,clauses,position,handed,expiry-status,caphit,skater-stats,goalie-stats&pg={page}"
    soup = Soup.get(url)
    pdf = pd.read_html(str(soup.find("table")))[0]
    df = df.append(pdf)
    time.sleep(0.5)

df["PLAYER"] = df["PLAYER"].apply(
    lambda x: re.split("\d{1}|\d{2}|\d{3}", x)[-1].replace(". ", "")
)
df["SALARY"] = df["SALARY"].apply(lambda x: x.replace("$", "").replace(",", ""))
df["SALARY"] = df["SALARY"].apply(float)
df.columns = ["name", "age", "salary"]
df = df.reset_index(drop=True)

df.to_csv("data/info-capfriendly_com.csv", index=False)
