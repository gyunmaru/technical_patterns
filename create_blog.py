# %%

import time
from sqlite3 import connect
import numpy as np
import pandas as pd
import os
import sys
import json
import datetime
from utils import code2name, ohlc_, codes_
from dbhelper import dbhelper as db
from wp_upload_helper import post_article
import html

# %%

with open("./info.json", "rb") as f:
    info_ = json.load(f)

# %%

ymdhms = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
print(ymdhms)
hizuke = datetime.datetime.now().strftime("%Y年%m月%d日")

# %%
parts = []

# %%
with open("./wp_template", "r") as f:
    parts.append(f.read())

with open("./wp_template_charts", "r") as f:
    template = f.read()

with open("./wp_template_news", "r") as f:
    template_news = f.read()


# %%
uploaded = pd.read_csv("./uploaded_files.csv", index_col=0)
uploaded

# %%

news = db.sqldb("TechDb", "select * from news")

# %%
for i, row in uploaded.iterrows():
    name = code2name(row.Symbols)
    parts.append(template.format(name, row.url))

    news_ = news.query(f" Symbols == '{row.Symbols}'")
    news_ = news_.reset_index(drop=True)
    nt = template_news.format(
        news_.lnk[0], news_.lnk[0],
        html.escape(news_.news[0].replace("\u3000", " ")),
        news_.lnk[1], news_.lnk[1],
        html.escape(news_.news[1].replace("\u3000", " ")),
        news_.lnk[2], news_.lnk[2],
        html.escape(news_.news[2].replace("\u3000", " ")),
    )

    parts.append(nt)

parts

# %%
content = "".join(parts)

# %%
"""
WordPress do not handle apostrophe 
(single quote, ', &apos;, &#039; ) well.
Til I find a way to handle single quot, i opt to use 
double quot (", &quot; , &#034; )
"""


# %%
res = post_article(
    info_['url'], info_['usr'], info_['ps'],
    'draft', f"{ymdhms}", f"本日のチャート{hizuke}",
    content=content
    # content="abc\u3000def"
)

# %%
with open("html_content.html", "w") as f:
    f.write(content)

# %%
debug_mode = True
if debug_mode:
    report = ""
    for i in range(1, len(parts)):

        res = post_article(
            info_['url'], info_['usr'], info_['ps'],
            'draft', f"{ymdhms}", f"parts{i}",
            # content="".join(parts[:i])
            content=parts[i]
            # content=content
        )

        if res.status_code != 201:
            report += f"parts {i:2d}: status {res.status_code}\n"
            break

        time.sleep(10)

    print(report)
    # print("".join(parts[:i]))
