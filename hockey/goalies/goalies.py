import re
import sqlite3
import string
from urllib import parse

import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/50.0.2661.102 Safari/537.36'
    }

url = 'https://leftwinglock.com/starting-goalies/index.php'
date = str(pd.Timestamp('now').date())

response = requests.get(url, params={'date': date}, headers=headers)
soup = BeautifulSoup(response.text)

containers = soup.find_all('div', class_='comparison__person')
goalies = {}
for container in containers:
    status = container.find(class_='comparison__person-wrapper-info').get_text().strip()
    name = (
        parse.parse_qs(
            container.find('span', class_='comparison__person-first-name')
            .a
            .attrs
            .get('href'))
            .get('../players/index.php?p1')[0]
    )
    goalies[name] = status

pd.DataFrame(goalies, index=['status']).T.reset_index()

import sqlite3

con = sqlite3.connect('data/hockey.db')
cur = con.cursor()

pd.read_sql('select * from')


#
