import pandas as pd

from season.schedule import pivot_schedule
from season.projections import projections
from season.league import League

schedule = pivot_schedule()

league, team = 84778, 12
proj = projections(league, team)
df = pd.merge(proj, schedule, how="left", on="team")

# Checkup

league = League(df)
league.team
league.fill()
league.check_all("")

league.available.sort_values("off_day_score", ascending=False)


##



#
