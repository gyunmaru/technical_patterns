# %%
import code
import numpy as np
import pandas as pd
from utils import ohlc_, codes_
from dbhelper import dbhelper as db
import talib as ta
import datetime
import os
import sys
import sqlite3

# if __name__ == "__main__":
#     import importlib
#     importlib.reload(sys.modules['utils'])
#     os.chdir("/workspaces/technical_patterns/")

# %%
DBNAME = "TechDb"
codes = codes_()

# %%
cd = datetime.datetime.today().date().strftime('%Y-%m-%d')
with sqlite3.connect(DBNAME) as conn:
    cur = conn.cursor()
    cur.execute(f"delete from patterns where calc_date == '{cd}'"
                " and Strategy in ('GX_MACD','DX_MACD')")
    conn.commit()
    cur.close()

# %%


for code in codes:

    prices = ohlc_(code)
    macd, macd_sig, macd_hist = ta.MACD(
        prices.Close.values.astype(np.float64), fastperiod=12,
        slowperiod=26, signalperiod=9
    )
    macd = pd.Series(macd)
    macd_sig = pd.Series(macd_sig)
    macd_hist = pd.Series(macd_hist)
    chg = macd.diff(3)
    chg_sig = macd_sig.diff(3)
    golden = (macd_hist >= 0) & (macd_hist.shift(1) < 0)
    golden = golden.fillna(False)
    golden = golden & (chg > 0) & (chg_sig > 0)
    dead = (macd_hist <= 0) & (macd_hist.shift(1) > 0)
    dead = dead.fillna(False)
    dead = dead & (chg < 0) & (chg_sig < 0)

    if golden.sum() > 0 | dead.sum() > 0:
        tmp = prices\
            .reset_index()\
            .reset_index()\
            .rename(columns={'Date': 'date', 'index': 'day_num'})\
            .loc[golden, ['date', 'day_num', 'Close']]

        tmp['Symbols'] = code
        tmp['calc_date'] = cd
        tmp['HP'] = f'{{"fast":12,"slow":26,"signal":9}}'

        dfs = []
        if golden.sum() > 0:
            df = tmp.loc[golden, :]
            df = df.copy()
            df['Strategy'] = 'GX_MACD'
            df['no'] = list(range(golden.sum()))
            dfs.append(df)
        if dead.sum() > 0:
            df = tmp.loc[dead, :]
            df = df.copy()
            df['Strategy'] = 'DX_MACD'
            df['no'] = list(range(dead.sum()))
            dfs.append(df)
        db.write2db(DBNAME, 'patterns',
                    pd.concat(dfs), if_exists='append'
                    )
