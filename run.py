import sqlite3
import pandas as pd

from projections import espn, fantasy_pros, fantasy_sharks, numberfire
from active import rosters
from utils.week import week

data_espn = espn.load('all')
# data_fantasy_pros = fantasy_pros.load('all')
data_fantasy_sharks = fantasy_sharks.load('all')
data_numberfire = numberfire.load('all')
