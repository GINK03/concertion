from lxml.html.clean import Cleaner
import warnings
import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor 
import concurrent 
import time
import glob
from pathlib import Path
import pickle
import sys
from urllib.parse import urlparse
import shutil
from bs4 import BeautifulSoup
import datetime
import requests
import glob
import re
import pandas as pd
from tqdm import tqdm
from os import environ as E
from typing import Tuple, List, Dict, Union

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f'{TOP_DIR}')
    from Web.Structures import TitleUrlDigestScore
    from Web.Structures import YJComment
    from Web import QueryToDict
    from Web import GetDigest
except Exception as exc:
    raise Exception(exc)
warnings.simplefilter("ignore")

'''
Twitterの魚拓サービス
個別TweetのURLを引数に画像、テキスト、css、アイコンをlocalにスナップショットを取る
複数回のデータのアップグレードは対応しない
'''


def put_local_html(url: str, date: str) -> Tuple[str, str]:
    """
    1. reflect htmlでパースできるように、ローカルディスクにフラッシュする
    2. stdoutは出さなくてもいいかもしれない
    return: Tuple[str, str]
    date: str, "YYYY-mm-dd"のフォーマットでstr型で入ってくる必要がある
    """
    if len(date) > len("YYYY-mm-dd"):
        raise Exception(f"date file format must be 'YYYY-mm-dd':str, {date}")
    digest = GetDigest.get_digest(url)
    raw_html = f'''<html>
<body>
<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">ご飯いきましょう？あたし朝まで空いてますよ。ふふ。<a href="{url}"> </a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</body>
</html>'''
    Path(f'{TOP_DIR}/var/Twitter/input/{date}/').mkdir(exist_ok=True, parents=True)
    with open(f'{TOP_DIR}/var/Twitter/input/{date}/{digest}', 'w') as fp:
        fp.write(raw_html)
    if E.get("DEBUG"):
        print(f'[{FILE}] putting local html, digest is {digest} url is {url}')
    return (url, digest)


def read_csv_and_put_to_local():
    """
    1. Pipeline.pyから呼ばれることを期待
    2. 最新のバズを検出するため
    3. top 2とかで処理している
    """
    df = pd.read_csv(f'{TOP_DIR}/var/FetchRecentBuzzTweets.csv')
    df = df[df.freq >= 2]
    df = df.head(20)
    # print(df)
    for url, date in zip(df.link, df.date):
        put_local_html(url, date)

def read_csv_batch_backlog_and_put_to_local(path_str=None):
    """
    1. twitter_batch_backlogsは別のプロセスにより生成される
    2. 参考: analytics_favorited_tweets_000_count_freq.py
    3. すべてのファイルをスキャンする必要はなく、latest top 3程度でよい
    """
    for fn in tqdm(sorted(glob.glob(f"{path_str}/*/*"))[-3:], desc=f"[{FILE}] flashing to local... "):
        df = pd.read_csv(fn)
        df = df.head(100)
        for url, date in zip(df.link, df.date):
            put_local_html(url, date)

if __name__ == '__main__':
    # put_local_html('https://twitter.com/kagamiisukeee/status/1228872466916769792')
    read_csv_and_put_to_local()
    # read_csv_batch_backlog_and_put_to_local()
