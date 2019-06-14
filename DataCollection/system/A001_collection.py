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
def pmap(arg):
    ii = arg['arg']
    for idx, i in enumerate(ii):
        try:
            print('now deal with', idx, len(ii))
            url = f'https://togetter.com/li/{i}'
            # - DELTEDされていたら取得しない
            if is_deleted(url):
                continue
            # - 5回以上スクレイピングされていたら取得しない
            if is_over_5times(url):
                continue
            r = requests.get(url)
            soup = bs4.BeautifulSoup(r.text)
            if soup.find('div', {'class':'alert alert-info'}) is not None:
                save(url, {'DELETED':True})
                continue
            if not Path(get_hashed_fs(url)).exists():
                save(url, {'LAST_UPDATE': datetime.datetime.now(), 'HTMLS':[], 'DELETED':False})
            print(soup.title.text, url, datetime.datetime.now())
            update_html(url, {'DATE':datetime.datetime.now(), 'HTML': r.text})
        except Exception as ex:
            print(ex)


def run():
    max_post_id = get_seeds()
    args = [[i] for i in reversed(range(int(max_post_id) - 10000 * 5, int(max_post_id)))]
    keys = [i[0]%16 for i in args]
    df = pd.DataFrame({'arg':args, 'key':keys}).groupby(by=['key']).sum().reset_index()
    args = df.to_dict('records')
    print(args)
    #[pmap(arg) for arg in args]
    with PPE(max_workers=16) as exe:
        exe.map(pmap, args)
if __name__ == '__main__':
    run()
