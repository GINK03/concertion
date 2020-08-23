import os
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
from tqdm import tqdm
from urllib.parse import urlparse

import base64
from os import environ as E
from typing import Union, Tuple, Dict, List

FILE = Path(__file__).name
NAME = Path(__file__).name.replace(".py", "")
TOP_DIR = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f"{TOP_DIR}")
    from Web.Structures import TitleUrlDigestScore
    from Web.Structures import YJComment
    from Web import QueryToDict
    from Web import GetDigest
except Exception as exc:
    raise Exception(exc)
warnings.simplefilter("ignore")

headers = {"User-Anget": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.88 Safari/537.36"}


def reflect_html(key: int, day: str, digest: str) -> Union[None, bool]:
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    """
    1. すでに処理したファイルが存在していたらスキップ
    """
    out_filename = f"{TOP_DIR}/var/Twitter/tweet/{day}/{digest}"
    if Path(out_filename).exists():
        return True
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1024x1024")
    options.add_argument(f"user-data-dir=/tmp/{FILE.replace('.py', '')}_{key:06d}")
    options.binary_location = shutil.which("google-chrome")
    try:
        driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
        driver.get(f"http://localhost/twitter/input/{day}/{digest}")
        print('ebug', f"http://localhost/twitter/input/{day}/{digest}")
        html = driver.page_source
        time.sleep(5)
        html = driver.page_source
        driver.save_screenshot(f"/home/gimpei/{digest}.png")
        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
        # elm = driver.find_element_by_xpath("/html")
        time.sleep(1)
        inner_html = driver.page_source
        # print("inner", inner_html)

        # inner_html = driver.page_source
        # print(html)
        """get shadow-root"""
        # elm = driver.execute_script("""return document.querySelector("twitter-widget").shadowRoot""")
        # elm = driver.execute_script("""return document.querySelector("twitter-widget").shadowRoot""")
        # inner_html = elm.get_attribute("innerHTML")
        cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)
        # print(inner_html)
        soup = BeautifulSoup(inner_html, "lxml")
        imported_csses = [el for el in soup.find_all("style", {"type": "text/css"})]

        # replace css text to local css
        for css in imported_csses:
            if "@import url" in css.text:
                css_url = re.search(r'url\("(.*?)"\)', css.text).group(1)
                css_digest = GetDigest.get_digest(css_url)
                # print(css_url, css_digest)
                with requests.get(css_url) as r:
                    css_text = r.text
                Path(f"{TOP_DIR}/var/Twitter/css").mkdir(exist_ok=True, parents=True)
                with open(f"{TOP_DIR}/var/Twitter/css/{css_digest}", "w") as fp:
                    fp.write(css_text)
                css.string = f'@import url("/twitter/css/{css_digest}")'

        # replace image src
        for img in soup.find_all(attrs={"src": True}):
            url = img.get("src")
            o = urlparse(url)
            if o.scheme == "":
                o = o._replace(scheme="https")
            url = o.geturl()

            url_digest = GetDigest.get_digest(url)
            if "format=jpg" in url or re.search(".jpg$", url) or re.search(".jpeg$", url) or re.search(".JPG$", url):
                with requests.get(url, timeout=30) as r:
                    binary = r.content
                Path(f"{TOP_DIR}/mnt/twitter_jpgs").mkdir(exist_ok=True, parents=True)
                with open(f"{TOP_DIR}/mnt/twitter_jpgs/{url_digest}", "wb") as fp:
                    fp.write(binary)
                # print(f"downloaded! {TOP_DIR}/mnt/twitter_jpgs/{url_digest}")
                img["src"] = f"/twitter/jpgs/{url_digest}"
            elif "format=png" in url or re.search(".png$", url):
                with requests.get(url, timeout=30) as r:
                    binary = r.content
                Path(f"{TOP_DIR}/var/Twitter/pngs").mkdir(exist_ok=True, parents=True)
                with open(f"{TOP_DIR}/var/Twitter/pngs/{url_digest}", "wb") as fp:
                    fp.write(binary)
                img["src"] = f"/twitter/pngs/{url_digest}"
            elif "normal" in url or ".js" in url or ".svg" in url:
                continue
            else:
                continue
                # raise Exception(f"unsupported image! url={url}")

        """adhoc style edit"""
        if soup.find(attrs={"class": "EmbeddedTweet"}):
            soup.find(attrs={"class": "EmbeddedTweet"})["style"] = "margin: 0 auto; margin-top: 150px;"

        out_dir = f"{TOP_DIR}/var/Twitter/tweet/{day}"
        Path(out_dir).mkdir(exist_ok=True, parents=True)
        with open(f"{out_dir}/{digest}", "w") as fp:
            fp.write(soup.__str__())
        driver.close()
        # if E.get("DEBUG"):
        print(f"[{NAME}] ordinally done, day = {day} digest = {digest}, filename = {out_dir}/{digest}")
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{NAME}] exc = {exc}, tb_lineno = {tb_lineno}, day = {day}, digest = {digest}, filename = {out_filename}", file=sys.stderr)
        out_filename = f"{TOP_DIR}/var/Twitter/tweet/{day}/{digest}"
        Path(f"{TOP_DIR}/var/Twitter/tweet/{day}").mkdir(exist_ok=True, parents=True)
        # パースに失敗したやつを無視する時、有効にする
        # Path(out_filename).touch()
        time.sleep(5)
        return None
    return f"/twitter/tweet/{day}/{digest}"


def proc(arg: Tuple[int, str]) -> None:
    """
    Args:
        - arg: keyとなるユニークなworking dirと指示の値と、ファイル名のペア
    Returns:
        - nothing
    """
    try:
        key, fn = arg
        path = Path(fn)
        digest = path.name
        day = path.parent.name
        out_file = f"{TOP_DIR}/var/Twitter/tweet/{day}/{digest}"
        # if Path(out_file).exists():
        #    return
        ret = reflect_html(key, day, digest)
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] key = {key}, filename = {fn}, exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)


def glob_fs_and_work(NUM=300):
    """
    1. 最新のタイムディレクトリのツイートを取得する
    """
    day_dir = sorted(glob.glob(f"{TOP_DIR}/var/Twitter/input/*"))[-1]
    tweet_files = glob.glob(f"{day_dir}/*")
    # random.shuffle(tweet_files)
    # tweet_files = tweet_files[:NUM]

    args = [(idx % 16, tweet_file) for idx, tweet_file in enumerate(tweet_files)]
    # for arg in args:
    #    proc(arg)
    try:
        with ProcessPoolExecutor(max_workers=16) as exe:
            for ret in tqdm(exe.map(proc, args), desc=f"[{FILE}] glob_fs_and_work, now getting...", total=len(args)):
                ret
    except Exception as exc:
        print(f"[{FILE}] exc = {exc}", file=sys.stderr)


if __name__ == "__main__":
    glob_fs_and_work()
