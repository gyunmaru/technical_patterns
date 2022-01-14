import numpy as np
import pandas as pd
from dbhelper import dbhelper as db
import base64
from xhtml2pdf import pisa


def ohlc_(code: str) -> pd.DataFrame:

    DBNAME = "TechDb"
    sqlstr = f'select * '\
        f'  from OHLC '\
        f" where Symbols == '{code}' "

    prices = db.sqldb(DBNAME, sqlstr)
    prices = prices\
        .pivot(index="Date", columns="Attributes", values="value")\
        .loc[:, ['Open', 'High', 'Low', 'Close', 'Adj Close']]
    prices['Open'] = prices.Open/prices.Close * prices['Adj Close']
    prices['High'] = prices.High/prices.Close * prices['Adj Close']
    prices['Low'] = prices.Low/prices.Close * prices['Adj Close']
    prices['Close'] = prices['Adj Close']
    prices = prices.loc[:, ['Open', 'High', 'Low', 'Adj Close']]\
        .rename(columns={'Adj Close': 'Close'})

    return prices


def codes_() -> pd.Series:

    DBNAME = "TechDb"
    sqlstr = f"select Symbols from OHLC group by Symbols"
    codes = db.sqldb(DBNAME, sqlstr)
    codes = codes\
        .loc[codes.Symbols.str.match("[0-9]{4}\.T"), :]\
        .reset_index(drop=True)

    return codes.Symbols


def code2name(code):
    DBNAME = "TechDb"
    sqlstr = f"select 名称 from mv_ranking where コード == '{code[:-2]}' "
    return(db.sqldb(DBNAME, sqlstr).iloc[0, 0])


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        source_html,                # the HTML to convert
        dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return True on success and False on errors
    return pisa_status.err
