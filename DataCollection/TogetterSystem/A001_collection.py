import requests
import bs4
import json
import pickle
import datetime
from concurrent.futures import ProcessPoolExecutor as PPE
import itertools
import pandas as pd
import re
from hashlib import sha256
import pickle
import gzip
from pathlib import Path
from FSDB import *
import time

def pmap(arg):
    ii = arg['arg']
    for idx, i in enumerate(ii):
        try:
            url = f'https://togetter.com/li/{i}'
            # - DELTEDされていたら取得しない
            if is_deleted(url):
                continue
            # - 5回以上スクレイピングされていたら取得しない
            if is_over_5times(url):
                continue
            with requests.get(url) as r:
                soup = bs4.BeautifulSoup(r.text, 'lxml')
            if soup.find('div', {'class':'alert alert-info'}) is not None:
                save(url, {'DELETED':True})
                continue
            print('now deal with', idx, len(ii))
            time.sleep(1)
            
            if not Path(get_hashed_fs(url)).exists():
                save(url, {'LAST_UPDATE': datetime.datetime.now(), 'HTMLS':[], 'DELETED':False})
            print(soup.title.text, url, datetime.datetime.now())
            update_html(url, {'DATE':datetime.datetime.now(), 'HTML': r.text})
        except Exception as ex:
            print(ex)


def run():
    print(f'start {__file__}.')
    max_post_id = get_seeds()
    print(f'finish get_seed {__file__}.')
    NUM = 32
    args = [[i] for i in reversed(range(int(max_post_id) - 10000 * 50, int(max_post_id)))]
    keys = [i[0]%NUM for i in args]
    df = pd.DataFrame({'arg':args, 'key':keys}).groupby(by=['key']).sum().reset_index()
    args = df.to_dict('records')
    #[pmap(arg) for arg in args]
    with PPE(max_workers=NUM) as exe:
        exe.map(pmap, args)
if __name__ == '__main__':
    run()
