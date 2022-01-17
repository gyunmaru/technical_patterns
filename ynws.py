# %%
from bs4 import BeautifulSoup
import requests


# %%


html = requests.get('https://finance.yahoo.co.jp/quote/2914.T/news')

yahoo = BeautifulSoup(html.content, "html.parser")

# %%

# %%

print(yahoo.select("a._1dBeQ-Vn"))

# %%
with open("yfn", "w") as f:
    f.write(str(yahoo))
# %%
hdr = yahoo.select('a[data-ylk="pos:9"]>h1')[0].get_text()
lnk = yahoo.select('a[data-ylk="pos:9"]')[0]['href']

# %%
print(lnk)
