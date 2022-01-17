# %%

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dbhelper import dbhelper as db
import sqlite3

# %%


def scrape_from_yfnews(code):

    news = []
    lnks = []
    url = "https://finance.yahoo.co.jp/quote/{}/news"

    html = requests.get(url.format(code))
    yahoo = BeautifulSoup(html.content, "html.parser")

    for i in range(1, 4):
        news.append(
            yahoo.select(f'a[data-ylk="pos:{i}"]>h1')[0].get_text()
        )
        lnks.append(
            yahoo.select(f'a[data-ylk="pos:{i}"]')[0]['href']
        )

    return (news, lnks)


# %%
meigara = pd.read_csv("./uploaded_files.csv", index_col=0)
logs = dict(Symbols=[], news=[], lnk=[])

for i, row in meigara.iterrows():

    news, lnks = scrape_from_yfnews(row.Symbols)
    logs['Symbols'].extend([row.Symbols]*len(news))
    logs['news'].extend(news)
    logs['lnk'].extend(lnks)

logs = pd.DataFrame(logs)
# %%

with sqlite3.connect("TechDb") as conn:
    cur = conn.cursor()
    cur.execute("delete from news where 1 == 1")
    conn.commit()
    cur.close()

# %%

db.write2db("TechDb", "news", logs, if_exists="append")
