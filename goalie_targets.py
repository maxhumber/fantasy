from gazpacho import Soup

df = pd.read_html("https://www.hockey-reference.com/leagues/NHL_2021.html")[0]
df["GP"] = pd.to_numeric(df["GP"], errors="coerce")
df["GF"] = pd.to_numeric(df["GF"], errors="coerce")
df = df.dropna().copy()
df['goals_per_game'] = df['GF'] / df["GP"]
df = df.rename(columns={"Unnamed: 0": "team"})
df = df[["team", "goals_per_game"]]
df.sort_values("goals_per_game")
gpg = df

df = pd.read_html("https://www.hockey-reference.com/leagues/NHL_2021_games.html")[0]
df['date'] = pd.to_datetime(df["Date"])
df = df[df['date'] >= '2021-04-19']
df = df[['Date', "Home", "Visitor"]]

df = pd.merge(df, gpg, how='left', left_on="Visitor", right_on="team")
df.groupby("Home")['goals_per_game'].mean().reset_index().sort_values("goals_per_game")
