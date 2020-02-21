from collections import namedtuple
import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
import shutil
from pathlib import Path
import datetime
import pickle
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import concurrent
from tqdm import tqdm
from inspect import currentframe, getframeinfo
from os import environ as E
import warnings
import random

warnings.filterwarnings("ignore")

FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
OUT_FOLDER = Path(f"{TOP_FOLDER}/var/YJ/frequency_watch")
OUT_FOLDER.mkdir(exist_ok=True, parents=True)

try:
    import sys

    sys.path.append(f"{TOP_FOLDER}")
    from Web import Gyotaku
    from Web import GetDigest
    from Web.Structures import TitleUrlDigestScore
except Exception as exc:
    raise Exception(exc)


def process(arg):
    try:
        # print(a)
        title = arg.title
        url = arg.url
        category = arg.category
        blobs_digest = Gyotaku.gyotaku(url, arg.rank)
        score = 1 / (arg.rank + 1)

        url_digest = GetDigest.get_digest(url)
        now = datetime.datetime.now()
        title_url_digest_score = TitleUrlDigestScore(
            title=title,
            url=url,
            digest=blobs_digest,
            score=score,
            date=now,
            category=category,
        )
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        out_sub_folder = f"{OUT_FOLDER}/{arg.category}"
        Path(out_sub_folder).mkdir(exist_ok=True, parents=True)
        with open(f"{out_sub_folder}/{now_str}_{url_digest}.pkl", "wb") as fp:
            pickle.dump(title_url_digest_score, fp)
        if E.get("DEBUG"):
            print("finish", title, url)
    except Exception as exc:
        print(f"[{FILE}][{getframeinfo(currentframe()).lineno}] {exc}, {arg}", file=sys.stderr)


def get_with_requests(ranking_url: str):
    with requests.get(ranking_url) as r:
        html = r.text
    return html


ARG = namedtuple("ARG", ["category", "title", "url", "rank"])


def fetch_each_categories():

    RANKING_URLs = [
        ("ALL", "https://news.yahoo.co.jp/ranking/access/news"),
        ("DOMESTIC", "https://news.yahoo.co.jp/ranking/access/news/domestic"),
        ("WORLD", "https://news.yahoo.co.jp/ranking/access/news/world"),
        ("BUSINESS", "https://news.yahoo.co.jp/ranking/access/news/business"),
        # ('ENTERTAINMENT', 'https://news.yahoo.co.jp/ranking/access/news/entertainment'),
        # ('SPORTS', 'https://news.yahoo.co.jp/ranking/access/news/sports'),
        ("IT_SCIENCE", "https://news.yahoo.co.jp/ranking/access/news/it-science"),
        ("LIFE", "https://news.yahoo.co.jp/ranking/access/news/life"),
        ("LOCAL", "https://news.yahoo.co.jp/ranking/access/news/local"),
    ]

    args = []
    for category, url in RANKING_URLs:
        html = get_with_requests(url)
        soup = BeautifulSoup(html, "html5lib")

        for idx, a in enumerate(soup.find_all("a", {"class": "newsFeed_item_link"})):
            arg = ARG(
                category=category,
                title=a.find("div", {"class": "newsFeed_item_title"}).text,
                url=a.get("href"),
                rank=idx,
            )
            args.append(arg)
    random.shuffle(args)
    try:
        with ProcessPoolExecutor(max_workers=32) as exe:
            for ret in tqdm(
                exe.map(process, args, timeout=180), total=len(args)
            ):
                ret
    except concurrent.futures._base.TimeoutError as exc:
        print(
            f"[{FILE}][{getframeinfo(currentframe()).lineno}] timeout handled, {exc}",
            file=sys.stderr,
        )
    except Exception as exc:
        print(
            f"[{FILE}][{getframeinfo(currentframe()).lineno}] {exc}",
            file=sys.stderr,
        )


def run():
    fetch_each_categories()


if __name__ == "__main__":
    run()
