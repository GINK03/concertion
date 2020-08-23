from bs4 import BeautifulSoup
import glob
import sys
from pathlib import Path
import pandas as pd
import numpy as np

TOP = Path(__file__).resolve().parent.parent
FILE = Path(__file__).name

users = pd.read_csv(Path("~/.mnt/20/sda/matching.jp/var/CollectUsernameFromFavorites.csv"), nrows=100)
users = users.username.apply(lambda x: x.lower())


def get_buzz_tweet() -> str:
    html = '\n'.join(["a"])

    df = pd.read_csv(TOP / "var/latest_buzz.csv", nrows=10)

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


    for user in users:
        tmp = "<div>"
        tmp += f'<p><a href="/feat?user={user}">{user}さんの特徴</a> '
        tmp += f'<a href="/kigyo?user={user}">{user}さんの向いていいる企業</a></p>'
        tmp += "</div>"
        html += tmp

    #for status_url, c in zip(df["status_url"], df["c"]):
    #    html += f"""<blockquote class="twitter-tweet"><p lang="ja" dir="ltr"><a href="{status_url}"> </a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>\n"""

    return html
