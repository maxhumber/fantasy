import pandas as pd
import sqlite3
from weekly import espn
from utils.week import week

espn.load(week)

con = sqlite3.connect('data/projections.db')
cur = con.cursor()
