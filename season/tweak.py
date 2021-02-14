import pandas as pd

from season.schedule import pivot_schedule
from season.projections import projections
from season.league import League
from season.goalies import possible, available

# SET UP

league, team = 84778, 12

# SHEDULE - PULL ONCE

schedule = pivot_schedule()

# JOIN - EVERY LEAGUE

proj = projections(league, team)
df = pd.merge(proj, schedule, how="left", on="team")

# SKATERS

league = League(df)
league.team
league.fill()
league.check_all("")

# GOALIES - PULL ONCE

shortlist = possible()

# GOALIES - TWEAK

league = 84919

yag = available(league)
pd.merge(shortlist, yag, on="name", how="inner")



#
