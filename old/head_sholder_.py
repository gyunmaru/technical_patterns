# %%
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from collections import defaultdict

# %%

df = pd.read_csv("stock_OHLC.csv")
df


# %%

prices = df\
    .query("(Attributes=='Adj Close')&"
           "(Symbols=='7203.T')")\
    .loc[:, ['Date', 'value']]\
    .rename(columns={"value": "close"})\
    .set_index('Date')\
    .close


prices

# %%
smoothing = 3
window_range = 10

# %%

# https://alpaca.markets/learn/algorithmic-trading-chart-pattern-python/


def get_max_min(prices: pd.Series, smoothing: int, window_range: int):
    smooth_prices = prices.rolling(window=smoothing).mean().dropna()
    local_max = argrelextrema(smooth_prices.values, np.greater)[0]
    local_min = argrelextrema(smooth_prices.values, np.less)[0]
    price_local_max_dt = []
    for i in local_max:
        if (i > window_range) and (i < len(prices)-window_range):
            price_local_max_dt.append(
                prices.iloc[i-window_range:i+window_range].idxmax())
            # later we will drop duplicated points, faster than checking all
            # time points with checking only local maxima
    price_local_min_dt = []
    for i in local_min:
        if (i > window_range) and (i < len(prices)-window_range):
            price_local_min_dt.append(
                prices.iloc[i-window_range:i+window_range].idxmin())
    maxima = pd.DataFrame(prices.loc[price_local_max_dt])
    minima = pd.DataFrame(prices.loc[price_local_min_dt])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min.index.name = 'date'
    max_min = max_min.reset_index()
    max_min = max_min[~max_min.date.duplicated()]
    p = prices.reset_index()
    max_min['day_num'] = p[p['Date'].isin(max_min.date)].index.values
    max_min = max_min.set_index('day_num')['close']

    return max_min


# %%

smoothing = 3
window = 10

minmax = get_max_min(prices, smoothing, window)
minmax

# %%


def find_patterns(max_min):
    patterns = defaultdict(list)

    # Window range is 5 units
    for i in range(5, len(max_min)):
        window = max_min.iloc[i-5:i]

        # Pattern must play out in less than n units
        if window.index[-1] - window.index[0] > 100:
            continue

        a, b, c, d, e = window.iloc[0:5]

        # IHS
        if a < b and c < a and c < e and c < d and e < d and abs(b-d) <= np.mean([b, d])*0.02:
            patterns['IHS'].append((window.index[0], window.index[-1]))

    return patterns


patterns = find_patterns(minmax)
patterns
# %%
