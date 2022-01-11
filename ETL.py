# %%
import numpy as np
import pandas as pd
import pandas_datareader as data
import datetime
from dateutil.relativedelta import relativedelta
import sqlite3

# %%
dbname = "TechDb"
conn = sqlite3.connect(dbname)

# %%
conn.close()

# %%
url = "https://info.finance.yahoo.co.jp/ranking/?kd=4"
dfs = pd.read_html(url)

# %%
dfs[0].to_csv("./ranking_table.csv")

# %%
with sqlite3.connect(dbname) as conn:
    cur = conn.cursor()
    # dbのnameをsampleとし、読み込んだcsvファイルをsqlに書き込む
    # if_existsで、もしすでにexpenseが存在していたら、書き換えるように指示
    dfs[0].to_sql('mv_ranking', conn, if_exists='replace')

# %%
with sqlite3.connect(dbname) as conn:
    cur = conn.cursor()
    df = pd.read_sql('SELECT * FROM mv_ranking', conn)
    cur.close()
    print(df)

# %%
tdt = datetime.datetime.today().date()
yago = tdt - relativedelta(years=1)

print(tdt.strftime('%Y-%m-%d'), yago.strftime('%Y-%m-%d'))

# %%
codes = dfs[0].iloc[:, 1]
# %%

df = data.DataReader(
    (codes+".T").to_list(), 'yahoo',
    yago.strftime('%Y-%m-%d'), tdt.strftime('%Y-%m-%d')
)

# %%

df = pd.melt(df, ignore_index=False)
df.to_csv("stock_OHLC.csv")

# %%
with sqlite3.connect(dbname) as conn:
    cur = conn.cursor()
    df.to_sql('OHLC', conn, if_exists='replace')
    cur.close()


# %%
with sqlite3.connect(dbname) as conn:
    cur = conn.cursor()
    df = pd.read_sql('SELECT * FROM OHLC limit 30', conn)
    cur.close()
    print(df)

# %%
