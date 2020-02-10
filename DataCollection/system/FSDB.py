
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
from hashlib import sha256
import pickle
import gzip
from pathlib import Path

import requests
import bs4
import json
import pickle
import datetime
from concurrent.futures import ProcessPoolExecutor as PPE
import itertools
import pandas as pd
import re

HERE = Path(__file__).resolve().parent
Path(f'{HERE}/var/downloads').mkdir(exist_ok=True, parents=True)


def get_hashed_fs(url):
    hashed = sha256(bytes(url, 'utf8')).hexdigest()[:16]
    fn = f'{HERE}/var/downloads/{hashed}'
    return fn


def is_deleted(url):
    fn = get_hashed_fs(url)
    if not Path(fn).exists():
        return False
    obj = pickle.loads(gzip.decompress(open(fn, 'rb').read()))
    if obj['DELETED'] == True:
        return True
    else:
        return False


def is_over_5times(url):
    fn = get_hashed_fs(url)
    if not Path(fn).exists():
        return False
    obj = pickle.loads(gzip.decompress(open(fn, 'rb').read()))
    if len(obj['HTMLS']) >= 5:
        return True
    else:
        return False


def save(url, obj):
    fn = get_hashed_fs(url)
    # if not Path(fn).exists():
    open(fn, 'wb').write(gzip.compress(pickle.dumps(obj)))


def get(url):
    fn = get_hashed_fs(url)
    obj = pickle.loads(gzip.decompress(open(fn, 'rb').read()))
    return obj


def update_html(url, obj):
    fn = get_hashed_fs(url)
    obj_ = pickle.loads(gzip.decompress(open(fn, 'rb').read()))
    obj_['HTMLS'].append(obj)
    save(url, obj_)


def allowed_gai_family():
    """
      https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
     """
    family = socket.AF_INET
    # if urllib3_cn.HAS_IPV6:
    #    family = socket.AF_INET6 # force ipv6 only if it is available
    return family


urllib3_cn.allowed_gai_family = allowed_gai_family


def get_seeds():
    '''
    最も最近に投稿されたまとめから最大値を逆算する
    '''
    print(f'try to get_seed {__name__}.')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.131 Safari/537.36',
        'referer': 'https://www.google.com/'
    }
    r = requests.get('https://togetter.com/recent', headers=headers)
    print('aa')
    thumbs = bs4.BeautifulSoup(r.text, 'lxml').find('div', {'class': 'topics_box'}).find_all('a', {'class': 'thumb'})
    thumb = thumbs[0]
    max_url = thumb.get('href')
    max_post_id = re.search(r'https://togetter.com/li/(.*?$)', max_url).group(1)
    if max_post_id.isdigit() is False:
        raise Exception('There is any wrong to get latest id.')
    print(f'finish to get_seed {__name__}.')
    return max_post_id
