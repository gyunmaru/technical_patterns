# %%
import numpy as np
import pandas as pd
import datetime

# %%


class gdcross(object):

    def __init__(self):
        pass

    def __call__(self, prices: pd.DataFrame,
                 short_interval: int, long_interval: int):
        return(self.find_cross(
            prices, short_interval, long_interval
        ))

    @classmethod
    def find_cross(cls,
                   prices: pd.DataFrame,
                   short_interval: int, long_interval: int):

        s = prices['Close'].rolling(short_interval).mean()
        l = prices['Close'].rolling(long_interval).mean()
        cross = s > l
        golden = (cross != cross.shift(1)) & (cross == True)
        dead = (cross != cross.shift(1)) & (cross == False)

        df = pd.DataFrame(
            {'golden': golden, 'dead': dead,
             'short': s, 'long': l},
            index=prices.index
        )

        return df

    @classmethod
    def convert2dbschema(cls, df: pd.DataFrame, Symbols: str,
                         short_interval: int, long_interval: int
                         ) -> pd.DataFrame:

        cd = datetime.datetime.today().date().strftime('%Y-%m-%d')
        df = df.reset_index()

        tmpdfs = []
        for side in ['golden', 'dead']:
            tmp = df.loc[df[side], ['Date']]
            tmp['day_num'] = tmp.index.values
            tmp['Strategy'] = f'{side}_cross'
            tmp['Symbols'] = Symbols
            tmp['calc_date'] = cd
            tmp['HP'] = f"{{'short_interval':{short_interval},"\
                f"'long_interval':{long_interval}}}"
            tmp['no'] = list(range(len(tmp)))
            tmp = tmp.rename(columns={'Date': 'date'})
            tmp['Close'] = np.nan
            tmpdfs.append(tmp)

        return pd.concat(tmpdfs).reset_index(drop=True)

        # %%
if __name__ == "__main__":

    from utils import ohlc_, codes_
    from dbhelper import dbhelper as db
    import datetime
    import matplotlib.pyplot as plt
    DBNAME = "TechDb"

    cross = gdcross()

    codes = codes_()
    for code in codes:
        prices = ohlc_(code)
        res = cross(prices, 25, 75)

        if len(res) > 0:
            # print(res)
            # fig = plt.figure()
            # ax = fig.add_subplot(1, 1, 1)
            # prices.plot(y='Close', ax=ax)
            # ax.scatter(
            #     x=res.index,
            #     y=prices.Close.where(res.golden, np.nan),
            #     color='orange'
            # )
            # res.plot(y='short', color='green', style="--", ax=ax)
            # res.plot(y='long', color='red', style="-.", ax=ax)
            # plt.show()
            db.write2db(
                DBNAME,
                'patterns',
                cross.convert2dbschema(res, code, 25, 75),
                if_exists='append'
            )
