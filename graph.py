# %%
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly as py
from dbhelper import dbhelper as db
from utils import ohlc_, codes_
import numpy as np
import pandas as pd
import talib as ta

# %%
DBNAME = "TechDb"
codes = codes_()
colors = dict(
    avocado="#258039", yellow_paper="#F5BE41",
    aqua_blue="#31A9B8", tomato="#CF3721",
    cherry_red="#F70025", ice="#F7EFE2",
    marmalade="#F25C00", orange_juice="#F9A603",
    sage="#A1BE95", raspberry="#ED5752",
    electric_blue="#4897D8", banana="#FFDB5C",
    watermelon="#FA6E59", canteloupe="#F8A055",
    caviar="#F77604", lettuce="#B8D20B",
    salmon="#F56C57", black_seaweed="#231B12",
    illuminating="#F5DF4D", ultimate_gray="#939597",
    chartreuse="#98C01C", bubblegum="#FA6775"

)

# %%


def add_candle(prices, code: str):
    return(
        go.Candlestick(x=prices.index.values,
                       open=prices.Open,
                       high=prices.High,
                       low=prices.Low,
                       close=prices.Close,
                       name=code,
                       increasing_line_color=f"{colors['chartreuse']}",
                       decreasing_line_color=f"{colors['bubblegum']}"
                       )
    )


def add_ma(prices, interval: int, line_dict={}):
    """
        memo
            Scatter, line argument
                dash -> 'dash' or 'dot'
    """

    ma = prices['Close'].rolling(interval).mean()
    return(
        go.Scatter(x=prices.index.values, y=ma.values, line=line_dict,
                   name=f"MA{interval}"

                   )
    )


def add_golden_cross(prices, pat):

    tmp = prices.loc[pat.query("Strategy=='golden_cross'").date, ['Close']]
    cel = prices.Close.max()
    y = tmp.Close + (cel-tmp.Close)*0.5

    return(
        go.Scatter(x=tmp.index, y=y, mode="markers",
                   marker_symbol="triangle-down", marker_size=20,
                   marker_color=colors['illuminating'],
                   name="goldenX"
                   )
    )


def add_dead_cross(prices, pat):

    tmp = prices.loc[pat.query("Strategy=='dead_cross'").date, ['Close']]
    if len(tmp) > 1:
        tmp = tmp.iloc[1:, :]
    bot = prices.Close.min()
    y = tmp.Close - (-bot+tmp.Close)*0.5

    return(
        go.Scatter(x=tmp.index, y=y, mode="markers",
                   marker_symbol="triangle-up", marker_size=20,
                   marker_color=colors['ultimate_gray'],
                   name="deadX"
                   )
    )


def add_macd(prices):

    macd, macd_sig, macd_hist = ta.MACD(
        prices.Close.values, fastperiod=12,
        slowperiod=26, signalperiod=9)

    return([
        go.Scatter(x=prices.index, y=macd, name='MACD',
                   line=dict(color='cornflowerblue', width=1)),

        go.Scatter(x=prices.index, y=macd_sig,
                   name='MACD(SIG)', line=dict(color='red', width=1))
    ])


def add_RSI(prices, timeperiod, name, line_dict):

    rsi = ta.RSI(prices.Close.values, timeperiod=timeperiod)

    return(
        go.Scatter(x=prices.index, y=rsi, name=name,
                   line=line_dict
                   )
    )


def add_IHS(prices, pat):

    cel = prices.Close.max()
    y = prices.loc[pat.date, "Close"]
    # y = y + (cel-y)*0.25

    return(
        go.Scatter(
            mode='markers', x=pat.date, y=y,
            marker=dict(symbol='circle', color=colors['cherry_red'], size=12,),
            name="IHS"
        )
    )


def get_gap(df):
    """
    gapとなっている時間を抽出し、リスト名timegapとして取得する
    """
    # gapの期間中を時間単位で補間したDataFrameを取得。max()は便宜上入れています。
    df.index = pd.to_datetime(df.index)
    df_resample = df.resample('1d').max()
    # 元々のindexとまとめてgapの時間以外を重複要素としてやる
    merged_index = df.index.append(df_resample.index)
    timegap = merged_index[~merged_index.duplicated(
        keep=False)]  # 重複要素を除去することでgapとなっている時間を抽出する

    return timegap


# %%


for code in codes:

    pats = db.sqldb(DBNAME, f"select * from patterns where "
                    f"Symbols='{code}'")

    if len(pats) == 0:
        continue
    if not ('golden_cross' in pats.Strategy.tolist()):
        continue
    if not ("IHS" in pats.Strategy.tolist()):
        continue

    prices = ohlc_(code)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.25, 0.25],
                        vertical_spacing=0.01)
    fig.add_trace(add_candle(prices, code),
                  row=1, col=1)
    fig.add_trace(add_ma(prices, 25, {'width': 2,
                                      "color": colors['aqua_blue']}), row=1, col=1)
    fig.add_trace(add_ma(prices, 75, {'width': 1,
                                      'color': colors['ultimate_gray']}), row=1, col=1)
    macd, macsig = add_macd(prices)
    fig.add_trace(macd, row=2, col=1)
    fig.add_trace(macsig, row=2, col=1)
    fig.add_trace(add_RSI(
        prices, 14, "RSI(14D)", line_dict=dict(
            color=colors['ultimate_gray'])
    ), row=3, col=1)
    fig.add_shape(go.layout.Shape(
        type="line", x0=prices.index.min(), y0=70,
        x1=prices.index.max(), y1=70,
        line=dict(color=colors['illuminating'], width=1, dash="dash"),),
        row=3, col=1
    )
    fig.add_shape(go.layout.Shape(
        type="line", x0=prices.index.min(), y0=30,
        x1=prices.index.max(), y1=30,
        line=dict(color=colors['illuminating'], width=1, dash="dash"),),
        row=3, col=1
    )

    timegap = get_gap(prices)

    if 'golden_cross' in pats.Strategy.tolist():
        fig.add_trace(add_golden_cross(
            prices, pats.query("Strategy=='golden_cross'")),
            row=1, col=1
        )

    if 'dead_cross' in pats.Strategy.tolist():
        fig.add_trace(add_dead_cross(
            prices, pats.query("Strategy=='dead_cross'")),
            row=1, col=1
        )

    if 'IHS' in pats.Strategy.tolist():
        fig.add_trace(add_IHS(
            prices, pats.query("Strategy=='IHS'")),
            row=1, col=1
        )

    fig.update_layout(
        margin=dict(
            autoexpand=False,
            l=60,
            r=100,
            t=20,
            b=20
        ),
        # showlegend=False,
        plot_bgcolor='white',
        xaxis_rangeslider_visible=False

    )
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.02,
    #     xanchor="right",
    #     x=1
    # ))

    fig.update_layout(legend=dict(font={'size': 10}))

    fig.update_xaxes(
        linecolor='LightGray',
        rangebreaks=[dict(values=timegap, dvalue=24*60*60*1000)]
    )
    fig.update_yaxes(linecolor='LightGray')
    fig.update_yaxes(title_text="値動き", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)

    fig.show()
    break

# %%
