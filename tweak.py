import pandas as pd

from season.schedule import pivot_schedule
from season.projections import projections
from season.league import League
from season.goalies import possible, available

# SCHEDULE - PULL ONCE

schedule = pivot_schedule()

# SET UP

league, team = 84919, 5

# JOIN - EVERY LEAGUE

proj = projections(league, team)
df = pd.merge(proj, schedule, how="left", on="team")

# SKATERS

sim = League(df)

sim.team
sim.fill()
sim.check_all("Clayton Keller")
sim.df
sim.add("Jake Muzzin")
sim.drop("Alexander Radulov")

# GOALIES - PULL ONCE

shortlist = possible()

# GOALIES - TWEAK

league = 84570

yag = available(league)
pd.merge(shortlist, yag, on="name", how="inner")



#
