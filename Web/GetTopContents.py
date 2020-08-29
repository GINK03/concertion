from bs4 import BeautifulSoup
import glob
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import random
TOP = Path(__file__).resolve().parent.parent
FILE = Path(__file__).name

users = pd.read_csv(Path("~/.mnt/20/sda/matching.jp/var/CollectUsernameFromFavorites.csv"), nrows=10000)

users = users.username.apply(lambda x: x.lower())


def get() -> str:
    html = '\n'.join(["a"])

    html = ""
    
    html += """
    <form action="/kigyo" method="post">
        <input type="text" name="user">
        <input type="submit" value="このtwitter idに向いている企業を検索">
    </form>
    <form action="/feat" method="post">
        <input type="text" name="user">
        <input type="submit" value="このtwitter idを特徴を検索">
    </form>
    """

    html += """<h3>有名人の特徴・お勧め企業</h3>"""
    
    for user in random.sample(users.tolist(), 10):
        tmp = "<div>"
        tmp += f'<p><a href="/feat?user={user}">{user}さんの特徴</a> '
        tmp += f'<a href="/kigyo?user={user}">{user}さんの向いていいる企業</a></p>'
        tmp += "</div>"
        html += tmp

    return html
