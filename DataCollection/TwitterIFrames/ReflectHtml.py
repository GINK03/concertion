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

headers = {'User-Anget': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.88 Safari/537.36'}


def reflect_html(key: int, day: str, digest: str):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument("window-size=1024x2024")
    options.add_argument(f"user-data-dir=/tmp/{FILE.replace('.py', '')}_{key:06d}")
    options.binary_location = shutil.which('google-chrome')
    try:
        driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
        driver.get(f'https://concertion.page/twitter/input/{day}/{digest}')
        time.sleep(2.0)
        html = driver.page_source
        '''get shadow-root'''
        elm = driver.execute_script('''return document.querySelector("twitter-widget").shadowRoot''')
        inner_html = elm.get_attribute('innerHTML')
        cleaner = Cleaner(style=True,
                          links=True,
                          add_nofollow=True,
                          page_structure=False,
                          safe_attrs_only=False)
        # print(inner_html)
        soup = BeautifulSoup(inner_html, 'lxml')
        imported_csses = [el for el in soup.find_all('style', {'type': 'text/css'})]

        # replace css text to local css
        for css in imported_csses:
            if '@import url' in css.text:
                css_url = re.search(r'url\("(.*?)"\)', css.text).group(1)
                css_digest = GetDigest.get_digest(css_url)
                # print(css_url, css_digest)
                with requests.get(css_url) as r:
                    css_text = r.text
                Path(f'{TOP_DIR}/var/Twitter/css').mkdir(exist_ok=True, parents=True)
                with open(f'{TOP_DIR}/var/Twitter/css/{css_digest}', 'w') as fp:
                    fp.write(css_text)
                css.string = f'@import url("/twitter/css/{css_digest}")'

        # replace image src
        for img in soup.find_all(attrs={'src': True}):
            url = img.get('src')
            o = urlparse(url)
            if o.scheme == '':
                o = o._replace(scheme='https')
            url = o.geturl()

            url_digest = GetDigest.get_digest(url)
            # print('img url', url)
            if 'format=jpg' in url or re.search('.jpg$', url) or re.search('.jpeg$', url) or re.search('.JPG$', url):
                with requests.get(url, timeout=30) as r:
                    binary = r.content
                Path(f'{TOP_DIR}/var/Twitter/jpgs').mkdir(exist_ok=True, parents=True)
                with open(f'{TOP_DIR}/var/Twitter/jpgs/{url_digest}', 'wb') as fp:
                    fp.write(binary)
                img['src'] = f'/twitter/jpgs/{url_digest}'
            elif 'format=png' in url or re.search('.png$', url):
                with requests.get(url, timeout=30) as r:
                    binary = r.content
                Path(f'{TOP_DIR}/var/Twitter/pngs').mkdir(exist_ok=True, parents=True)
                with open(f'{TOP_DIR}/var/Twitter/pngs/{url_digest}', 'wb') as fp:
                    fp.write(binary)
                img['src'] = f'/twitter/pngs/{url_digest}'
            elif 'normal' in url:
                continue
            else:
                raise Exception(f'unsupported image! url={url}')

        '''adhoc style edit'''
        if soup.find(attrs={'class': 'EmbeddedTweet'}):
            soup.find(attrs={'class': 'EmbeddedTweet'})['style'] = 'margin: 0 auto; margin-top: 150px;'

        out_dir = f'{TOP_DIR}/var/Twitter/tweet/{day}'
        Path(out_dir).mkdir(exist_ok=True, parents=True)
        with open(f'{out_dir}/{digest}', 'w') as fp:
            fp.write(soup.__str__())
        driver.close()
        print(f'ordinally done, {day} {digest}')
        # driver.quit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        out_filename = f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}'
        Path(f'{TOP_DIR}/var/Twitter/tweet/{day}').mkdir(exist_ok=True, parents=True)
        Path(out_filename).touch()
        print(f'[refrect] {exc} exc line = {exc_tb.tb_lineno}, {day}, {digest}', file=sys.stderr)
    return f'/twitter/tweet/{day}/{digest}'


def proc(arg):
    try:
        key, fn = arg
        path = Path(fn)
        digest = path.name
        day = path.parent.name
        out_file = f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}'
        if Path(out_file).exists():
            return
        # print('digest day', digest, day)
        ret = reflect_html(key, day, digest)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f'[{FILE}] {key}, {fn}, {exc}, exc line = {exc_tb.tb_lineno}', file=sys.stderr)


def glob_fs_and_work():
    fns = glob.glob(f'{TOP_DIR}/var/Twitter/input/*/*')
    if E.get('ALL'):
        random.shuffle(fns)
        fns = fns
        NUM = 64
    else:
        fns = sorted(fns)[-300:]
        NUM = 16
    args = [(idx % NUM, fn) for idx, fn in enumerate(fns)]
    for i in tqdm(range(0, len(args), NUM), total=len(args)//NUM):
        os.system('pgrep chrome | xargs kill -9')
        try:
            with ProcessPoolExecutor(max_workers=NUM) as exe:
                for ret in exe.map(proc, args[i:i+NUM]):
                    ret
        except Exception as exc:
            print(exc)

if __name__ == '__main__':
    glob_fs_and_work()
