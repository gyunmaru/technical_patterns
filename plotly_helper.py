# %%
import pandas as pd
import plotly as py
import plotly.graph_objects as go
from dbhelper import dbhelper as db
import base64
from xhtml2pdf import pisa


# %%
DBNAME = "TechDb"


# %%

def ohlc_(code: str):
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


# %%
# get pattern list
pats = db.sqldb(DBNAME, "select * from patterns")
pid = pats\
    .groupby(['Strategy', 'Symbols', 'calc_date', 'HP', 'no'])\
    .agg({'date': max})\
    .index
pid

# %%
# print to pdf
figures = []

for i in range(len(pid)):
    st, sy, cd, hp, no = pid[i]

    pat = pats.query(f"(Strategy=='{st}') &"
                     f" (Symbols=='{sy}') &"
                     f" (calc_date=='{cd}')&"
                     f' (HP=="{hp}")&'
                     f" (no=={no})"
                     )
    prices = ohlc_(sy)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=prices.index.values,
                                 open=prices.Open,
                                 high=prices.High,
                                 low=prices.Low,
                                 close=prices.Close,
                                 name=cd))
    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=pat.date,
            y=prices.loc[pat.date, "Close"],
            marker=dict(
                symbol='circle-open',
                color='rgba(255, 223, 0, 0.8)',
                size=8,
            ),
            line=dict(width=3),
            showlegend=False
        )
    )

    fig.update_layout(showlegend=False)
    fig.update_layout(
        title=sy,
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        ),
        margin=dict(l=80, r=80, t=100, b=80)
    )

    figures.append(fig)


# %%
width = 600
height = 600

template = (''
            '<img style="width: {width}; height: {height}"'
            ' src="data:image/png;base64,{image}">'
            # Optional caption to include below the graph
            # '{caption}'
            # '<br>'
            '<hr>'
            '')

# A collection of Plotly graphs
# figures

# Generate their images using `py.image.get`
images = [base64.b64encode(
    py.io.to_image(figure, width=width, height=height)
).decode('utf-8') for figure in figures]

report_html = ''
for image in images:
    _ = template
    _ = _.format(image=image,  width=width, height=height)
    report_html += _

# display(HTML(report_html))
convert_html_to_pdf(report_html, 'monitor.pdf')

# %%
