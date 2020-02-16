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

try:
    FILE = Path(__file__).name
    TOP_FOLDER = Path(__file__).resolve().parent.parent
    sys.path.append(f'{TOP_FOLDER}')
    from Web import GetDigest
    from Web import Hostname
    from Web.Structures import DataType
except Exception as exc:
    raise Exception(exc)


def replace_with_digest(html, child_url, digest):
    # このコード上ではdomainがnot sureなので、skip
    relative = f'/blobs/'+digest
    return html.replace(f'"{child_url}"', f'"{relative}"')
    return html


def get_children_and_replace_blobs(o_mst: urlparse, html: str, child_url: str, is_href=False):
    o = urlparse(child_url)

    if o.scheme == '':
        o = o._replace(scheme=o_mst.scheme)
    if o.netloc == '':
        o = o._replace(netloc=o_mst.netloc)
    o = o._replace(params='', query='', fragment='')

    digest = GetDigest.get_digest(o.geturl())
    if Path(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}').exists():
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
            data_type = DataType(data='no nedd', type=str)
        elif is_href is True:
            with requests.get(o.geturl(), timeout=5) as r:
                r.encoding = r.apparent_encoding
                text = r.text
            data_type = DataType(data=text, type=str)
        else:
            return html
    except Exception as exc:
        print(exc)
        data_type = DataType(data='error', type=str)
    with open(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(data_type)))
    print(child_url, digest)
    html = replace_with_digest(html, child_url, digest)
    return html


def gyotaku(url: str, instance_number: int):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1024x2024")
    options.add_argument(f"user-data-dir=/tmp/{FILE}_{instance_number:06d}")
    options.binary_location = shutil.which('google-chrome')
    driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
    # url = 'https://twitter.com/PFU_HHKB/status/1228147347567173632'
    o_mst = urlparse(url)
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'html5lib')
    for a in soup.find_all(attrs={'src': True}):
        html = get_children_and_replace_blobs(o_mst, html, a.get('src'))
    with open(f'{TOP_FOLDER}/var/Gyo/html', 'w') as fp:
        fp.write(html)
    # driver.save_screenshot(f"{TOP_FOLDER}/var/Gyo/screenshot.png")
    data_type = DataType(data=html, type=str)
    digest = GetDigest.get_digest(o_mst.geturl())
    print('transformed', o_mst.geturl(), digest)
    with open(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}', 'wb') as fp:
        fp.write(gzip.compress(pickle.dumps(data_type)))
    return digest
