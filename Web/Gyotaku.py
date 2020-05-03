import os
import shutil
from bs4 import BeautifulSoup
import time
import requests
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse
import sys
import gzip
import pickle
import re

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f'{TOP_DIR}')
    from Web import GetDigest
    from Web import Hostname
    from Web.Structures import DataType
except Exception as exc:
    raise Exception(exc)


def replace_with_digest(html: str, child_url: str, digest: str) -> str:
    """
    Args:
        - html
        - child_url
        - digest
    Returns:
        - html: 変換したHTML
    """
    relative = f'/blobs/'+digest
    return html.replace(f'"{child_url}"', f'"{relative}"')


def get_children_and_replace_blobs(o_mst: urlparse, html: str, child_url: str, is_href=False) -> str:
    """
    1. YJのコンテンツを自サイトのコンテンツに張り替える処理を行う
    2. 著作権的な側面はコメントを自由投稿にし、評論対象とする + 統計的処理を行い参照の体を必ず確保する
    Args:
        - o_mst: 親URLをurlparseしたもの
        - html: 親URLのhtml
        - child_url: 子URLでひも付きとなるもの
        - is_href:
    Returns:
        - html: 変換したHTML
    """
    o = urlparse(child_url)
    if o.scheme == '':
        o = o._replace(scheme=o_mst.scheme)
    if o.netloc == '':
        o = o._replace(netloc=o_mst.netloc)
    o = o._replace(params='', query='', fragment='')

    digest = GetDigest.get_digest(o.geturl())
    if Path(f'{TOP_DIR}/var/Gyo/blobs/{digest}').exists():
        html = replace_with_digest(html, child_url, digest)
        return html
    try:
        if re.search(r'(.jpg$|.gif$|.zip$)', o.geturl()):
            with requests.get(o.geturl(), timeout=5) as r:
                binary = r.content
            data_type = DataType(data=binary, type=bytes)
        elif re.search(r'(.js$|.txt$|.htm$|.html$)', o.geturl()):
            with requests.get(o.geturl(), timeout=5) as r:
                r.encoding = r.apparent_encoding
                text = r.text
            data_type = DataType(data=text, type=str)
        elif re.search(r'.js', o.geturl()):
            data_type = DataType(data='no need', type=str)
        elif is_href is True:
            with requests.get(o.geturl(), timeout=5) as r:
                r.encoding = r.apparent_encoding
                text = r.text
            data_type = DataType(data=text, type=str)
        else:
            return html
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
        data_type = DataType(data='error', type=str)
    with open(f'{TOP_DIR}/var/Gyo/blobs/{digest}', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(data_type)))
    html = replace_with_digest(html, child_url, digest)
    return html


def get_nexts(href: str) -> None:
    try:
        digest = GetDigest.get_digest(href)
        Path(f"{TOP_DIR}/var/YJ/NextPages/").mkdir(exist_ok=True, parents=True)
        if Path(f'{TOP_DIR}/var/YJ/NextPages/{digest}').exists():
            # load
            with open(f'{TOP_DIR}/var/YJ/NextPages/{digest}', 'rb') as fp:
                html = gzip.decompress(fp.read()).decode("utf8")
        else:
            with requests.get(href) as r:
                html = r.text
            # save
            with open(f'{TOP_DIR}/var/YJ/NextPages/{digest}', 'wb') as fp:
                fp.write(gzip.compress(bytes(html, "utf8")))
        next_soup = BeautifulSoup(html, "lxml")

        next_page_li = next_soup.find("li", attrs={"class": "next"})
        if next_page_li is not None and next_page_li.find("a") is not None:
            get_nexts(href=next_page_li.find("a").get("href"))
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)

def gyotaku(url: str, instance_number: int) -> str:
    """
    1. gyotakuというジェネリックな名前がついているが実際はYJ専用の取得関数
    2. コメント等が非同期でAjaxで実装されているので、seleniumで動く必要がある
    3. たまにコメントの取得に失敗するので、time.sleep(1) -> time.sleep(1.5)に変更
    Args:
        - url: 取得対象URL
        - instance_number: chromeのインスタンスは同一の設定・キャッシュファイルを同時に参照できないのでキャッシュファイルをユニークにするために指定する
    Returns:
        - digest: 取得対象URLのdigest
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("window-size=1024x2024")
    options.add_argument(f"user-data-dir=/tmp/{FILE}_{instance_number:06d}")
    options.binary_location = shutil.which('google-chrome')
    driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
    
    o_mst = urlparse(url)
    digest = GetDigest.get_digest(o_mst.geturl())
    """ もしすでに取得していたらReturnする """
    if Path(f'{TOP_DIR}/var/Gyo/blobs/{digest}').exists():
        return digest

    driver.get(o_mst.geturl())
    time.sleep(1.5)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'html5lib')
    for a in soup.find_all(attrs={'src': True}):
        html = get_children_and_replace_blobs(o_mst, html, a.get('src'))
    
    """ 次のページへがYJはたくさんあるので、まとめて取得する """
    next_page_li = soup.find("li", attrs={"class": "next"})
    if next_page_li is not None and next_page_li.find("a") is not None:
        get_nexts(href=next_page_li.find("a").get("href"))

    with open(f'{TOP_DIR}/var/Gyo/html', 'w') as fp:
        fp.write(html)
    data_type = DataType(data=html, type=str)
    print(f"[{FILE}] transformed, o_mst = {o_mst.geturl()}, digest = {digest}", file=sys.stdout)
    with open(f'{TOP_DIR}/var/Gyo/blobs/{digest}', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(data_type)))
    return digest
