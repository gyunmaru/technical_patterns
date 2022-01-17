# %%

if __name__ == "__main__":
    import sys
    import importlib
    importlib.reload(sys.modules['wp_upload_helper'])
    # import os
    # os.chdir("/workspaces/technical_patterns/")


import numpy as np
import pandas as pd
import glob
import re
import datetime
from dbhelper import dbhelper as db
from wp_upload_helper import header, upload_image_to_wordpress, post_article
import json
import sys


# %%

cd = datetime.datetime.today().strftime("%Y%m%d")
#----------------------------#
cd = "20220114"
#----------------------------#

htmls = glob.glob(f"./graph_html/*_{cd}.html")

with open('info.json', 'rb') as f:
    info_ = json.load(f)

hed = header(info_['usr'], info_['ps'])

files = dict(Symbols=[], file=[], url=[])

for html in htmls:
    res = upload_image_to_wordpress(html, info_['url'], hed)
    files['Symbols'].append(
        html.replace("./graph_html/", "")[:4] + ".T"
    )
    files['file'].append(html)
    files['url'].append(res.json()['guid']['rendered'])

# %%

pd.DataFrame(files).to_csv("./uploaded_files.csv")
