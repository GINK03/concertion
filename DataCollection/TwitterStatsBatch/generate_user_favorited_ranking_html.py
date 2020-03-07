import pandas as pd
from os import environ as E
from pathlib import Path
import numpy as np

HOME = E['HOME']

HERE = Path(__file__).resolve().parent

df = pd.read_csv(f'{HOME}/username_freq_jp_ranking.csv')
df = df.head(1000)

head = f'<html><head><title>Twitterファボランキング</title></head><body>'
body = ''
for username, freq in zip(df.username, df.freq):
    score = np.log1p(freq) 
    tmp = f'<p>{username} {score:0.3f}</p></br>'
    print(tmp)
    body += tmp

tail = '</body></html>'

with open(f'{HERE}/var/user_favorited_ranking.html', 'w') as fp:
    fp.write(head + body + tail)
