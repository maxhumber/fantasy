import pandas as pd

today = pd.Timestamp('today')
start = pd.Timestamp('2018-09-04')
week = (today - start).days // 7 + 1
