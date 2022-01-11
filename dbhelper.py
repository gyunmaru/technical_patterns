
# %%
import sqlite3
import pandas as pd


class dbhelper(object):

    def __init__(self):
        super(dbhelper, self).__init__()

    @classmethod
    def sqldb(cls, dbname, sql):
        with sqlite3.connect(dbname) as conn:
            cur = conn.cursor()
            df = pd.read_sql(sql, conn)
            cur.close()
        return df

    @classmethod
    def write2db(cls, dbname, tblname, df, if_exists: str = 'replace'):
        with sqlite3.connect(dbname) as conn:
            cur = conn.cursor()
            df.to_sql(tblname, conn, if_exists=if_exists)


# %%
if __name__ == "__main__":

    dbname = 'TechDb'
    print(
        dbhelper.sqldb(dbname, 'select * from OHLC limit 10')
    )

# %%
