
# %%

import json
import subprocess
from subprocess import PIPE
import os
import sys

wkdir = os.getcwd()
print(f" working directory {wkdir}")

# %%


def run_python_file(file_name, wkdir):

    proc = subprocess.run(['python', file_name],
                          cwd=wkdir, stdout=PIPE, stderr=PIPE
                          )
    print(proc.stdout.decode('utf-8').split('\n'))
    print(proc.stderr.decode('utf-8').split('\n'))

    return

# %%


with open(wkdir+"/config.json", 'rb') as f:
    config = json.load(f)
# %%
if config['ETL']:
    run_python_file('ETL.py', wkdir)

# %%

run_python_file('headsholder.py', wkdir)

# %%

run_python_file('goldencross.py', wkdir)

# %%

run_python_file('macd.py', wkdir)

# %%
run_python_file('graph.py', wkdir)

# %%

run_python_file('upload_graph_html.py', wkdir)
# %%

run_python_file('scrape_news.py', wkdir)
