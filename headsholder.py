# %%
import sqlite3
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from collections import defaultdict
import datetime

# %%


class HeadSholder(object):

    def __init__(self):
        pass

    @classmethod
    def __call__(cls):
        raise NotImplementedError()

    @classmethod
    def get_max_min(cls, prices: pd.DataFrame, smoothing: int,
                    window_range: int
                    ):
        r"""
            get_max_min

            Parameters
            -----------------------------
            prices: pandas.DataFrame
                OHLC type data frame
            smoothing : int
                smoothing parameter
                takes 'smoothing' moving average of closing price
            window_range: int
                window range to find local minima and maxima
        """

        smooth_prices = prices['Close'].rolling(
            window=smoothing).mean().dropna()
        local_max = argrelextrema(smooth_prices.values, np.greater)[0]
        local_min = argrelextrema(smooth_prices.values, np.less)[0]
        price_local_max_dt = []
        for i in local_max:
            if (i > window_range) and (i < len(prices)-window_range):
                price_local_max_dt.append(
                    prices.iloc[i-window_range:i+window_range]['Close'].idxmax())
                # later we will drop duplicated points, faster than checking all
                # time points with checking only local maxima
        price_local_min_dt = []
        for i in local_min:
            if (i > window_range) and (i < len(prices)-window_range):
                price_local_min_dt.append(
                    prices.iloc[i-window_range:i+window_range]['Close'].idxmin())
        maxima = pd.DataFrame(prices.loc[price_local_max_dt])
        minima = pd.DataFrame(prices.loc[price_local_min_dt])
        maxima['side'] = 'max'
        minima['side'] = 'min'
        max_min = pd.concat([maxima, minima]).sort_index()
        max_min.index.name = 'date'
        max_min = max_min.reset_index()
        max_min = max_min[~max_min.date.duplicated()]
        p = prices.reset_index()
        max_min['day_num'] = p[p['Date'].isin(max_min.date)].index.values
        max_min = max_min.set_index('day_num')[['date', 'Close', 'side']]

        return max_min


class IHS(HeadSholder):

    def __init__(self):
        pass

    @classmethod
    def __call__(cls, prices: pd.DataFrame, smoothing: int = 3,
                 window_range: int = 10
                 ):
        return cls.find_ihs(prices, smoothing, window_range)

    @classmethod
    def find_patterns_ihs(cls, max_min):
        patterns = []

        # Window range is 5 units
        for i in range(5, len(max_min)):
            window = max_min.iloc[i-5:i]

            # Pattern must play out in less than n units
            if window.index[-1] - window.index[0] > 100:
                continue

            a, b, c, d, e = window.Close.iloc[0:5]
            a_, b_, c_, d_, e_ = window.side.iloc[0:5]

            # IHS
            if a < b and c < a and c < e and c < d and e < d \
                and abs(b-d) <= np.mean([b, d])*0.02 and\
                a_ == 'min' and b_ == 'max' and c_ == 'min' and d_ == 'max' and\
                    e_ == 'min':
                patterns.append(window)

        return patterns

    @classmethod
    def find_ihs(cls, prices: pd.DataFrame, smoothing: int = 3,
                 window_range: int = 10
                 ):

        max_min = cls.get_max_min(prices, smoothing, window_range)
        return cls.find_patterns_ihs(max_min)


# %%
if __name__ == "__main__":

    from dbhelper import dbhelper as db
    dbname = "TechDb"
    cd = datetime.datetime.today().date().strftime('%Y-%m-%d')
    print(cd)
    with sqlite3.connect(dbname) as conn:
        cur = conn.cursor()
        cur.execute(f"delete from patterns where calc_date == '{cd}'")
        conn.commit()
        cur.close()

    smooths = [3, 3]
    windows = [10, 60]

    codes = db.sqldb(dbname,
                     "select Symbols from OHLC group by Symbols")
    codes = codes.Symbols
    ihs = IHS()

    for s, w in zip(smooths, windows):
        pats = {}
        for code in codes:
            sqlstr = f"select * from OHLC "\
                f" where Symbols == '{code}' "

            prices = db.sqldb(dbname, sqlstr)
            prices = prices\
                .pivot(index="Date", columns="Attributes", values="value")\
                .loc[:, ['Open', 'High', 'Low', 'Adj Close']]\
                .rename(columns={"Adj Close": "Close"})

            pat = ihs(prices, smoothing=s, window_range=w)
            if len(pat) > 0:
                pats[code] = pat

        for k, v in pats.items():
            for i, df in enumerate(v):
                df['Symbols'] = k
                df['calc_date'] = datetime.datetime.today().date()
                df['Strategy'] = 'IHS'
                df['HP'] = f"{{'smooth':{s},'window_range':{w}}}"
                df['no'] = i

                df = df.\
                    loc[:, ['Strategy', 'Symbols', 'calc_date',
                        'HP', 'no', 'date', 'Close']]

                db.write2db(dbname, 'patterns', df, 'append')


# %%
