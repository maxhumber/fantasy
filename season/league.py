from collections import Counter
import pandas as pd
import numpy as np

from utils import flatten


class League:
    def __init__(self, df):
        df = df.copy()
        df = df.sort_values("ranking_custom")
        self.df = df

    def __repr__(self):
        return f"League()"

    @property
    def dates(self):
        df = self.df
        return [
            date.strftime("%Y-%m-%d")
            for date in pd.to_datetime(df.columns, errors="coerce")
            if date >= pd.Timestamp("2020-01-01")
        ]

    @property
    def team(self):
        df = self.df
        df = df[~df["owner"].isin(["A", "DROP"])]
        return df

    @property
    def available(self):
        df = self.df
        df = df[df["owner"].isin(["A", "DROP"])]
        return df

    @property
    def transactions(self):
        df = self.df
        df = df[df["owner"].isin(["ADD", "DROP"])]
        return df

    def check(self, drop, add):
        team = self.team
        team = team[team["name"] != drop]
        available = self.available
        player = available[available["name"] == add]
        df = pd.concat([team, player])
        df = df.sort_values("ranking_custom")
        return df

    def add(self, name):
        df = self.df
        df.loc[df["name"] == name, "owner"] = "ADD"
        self.df = df

    def drop(self, name):
        df = self.df
        df.loc[df["name"] == name, "owner"] = "DROP"
        self.df = df

    @staticmethod
    def _fill(team_df_for_date):
        slots = Counter({"C": 2, "LW": 2, "RW": 2, "D": 4})
        roster = {k: [] for k in slots.keys()}
        for i, row in team_df_for_date.iterrows():
            name = row["name"]
            positions = row["position"].split(",")
            for position in positions:
                if name not in flatten(roster):
                    if slots.get(position) > 0:
                        slots[position] -= 1
                        roster.get(position).append(name)
        df = pd.DataFrame(roster.values(), roster.keys()).T.melt().dropna()
        df.columns = ["position", "name"]
        return df

    def fill(self, drop=None, add=None):
        df = self.team.copy()
        if drop or add:
            df = self.check(drop, add)
        df["starts"] = 0
        for date in self.dates:
            team_df_for_date = df[df[date] == 1]
            roster = self._fill(team_df_for_date)
            df.loc[df["name"].isin(roster["name"]), "starts"] += 1
        df["keep_score"] = (
            df["ranking_composite"].rank()
            + df["ranking_custom"].rank()
            + df["starts"].rank(ascending=False)
        )
        df["keep_score"] = df[["keep_score"]].apply(
            lambda x: (x - x.min()) / (x.max() - x.min())
        )
        df = df.sort_values("keep_score")
        df["keep_score"] = np.round(1 - df["keep_score"], 2)
        df = df[
            [
                "name",
                "position",
                "keep_score",
                "starts",
                "ranking_custom",
                "ranking_composite",
            ]
        ]
        return df

    def check_all(self, drop):
        df = self.available.copy()
        df["starts_marginal"] = 0
        df["keep_score"] = 0
        s = self.fill()["starts"].sum()
        for name in self.available["name"]:
            di = self.fill(drop=drop, add=name)
            ks = di["keep_score"]
            si = di["starts"].sum()
            df.loc[df["name"] == name, "starts_marginal"] = si - s
            df.loc[df["name"] == name, "keep_score"] = ks
        df = df[
            [
                "name",
                "team",
                "position",
                "starts_marginal",
                "ranking_custom",
            ]
        ]
        df = df.sort_values(
            ["starts_marginal", "ranking_custom"], ascending=[False, True]
        )
        df = df[df["starts_marginal"] >= 0]
        return df
