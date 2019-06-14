
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

Path('tmp/downloads').mkdir(exist_ok=True, parents=True)
def get_hashed_fs(url):
    hashed = sha256(bytes(url, 'utf8')).hexdigest()
    fn = f'tmp/downloads/{hashed}'
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
    #if not Path(fn).exists():
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

def get_seeds():
    '''
    最も最近に投稿されたまとめから最大値を逆算する
    '''
    r = requests.get('https://togetter.com/recent')
    thumbs = bs4.BeautifulSoup(r.text, 'lxml').find('div', {'class':'topics_box'}).find_all('a', {'class':'thumb'})
    thumb = thumbs[0]
    max_url = thumb.get('href')
    max_post_id = re.search(r'https://togetter.com/li/(.*?$)', max_url).group(1)
    if max_post_id.isdigit() is False:
        print('There is any wrong to get latest id.')
        exit(1)
    return max_post_id
