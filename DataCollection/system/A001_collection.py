import requests
import bs4
import json
import pickle
from sqlitedict import *
import datetime
from concurrent.futures import ProcessPoolExecutor as PPE
import itertools
import pandas as pd
import re
'''
TABLE DEFINITIONS
{
    'LAST_UPDATE': datetime,
    'HTMLS': [{'DATE':datetime, 'HTML':html }],
    'DELETED':boolean,
}
'''
def pmap(arg):
    ii = arg['arg']
    db = SqliteDict('db.sqlite', encode=pickle.dumps, decode=pickle.loads, autocommit=True)
    for idx, i in enumerate(ii):
        try:
            print('now deal with', idx, len(ii))
            url = f'https://togetter.com/li/{i}'
            # - DELTEDされていたら取得しない
            if db.get(url) is not None and db.get(url)['DELETED'] == True:
                continue
            # - 5回以上スクレイピングされていたら取得しない
            if db.get(url) is not None and len(db.get(url)['HTMLS']) >= 5:
                continue
            r = requests.get(url)
            soup = bs4.BeautifulSoup(r.text)
            if soup.find('div', {'class':'alert alert-info'}) is not None:
                db[url] = {'DELETED':True}
                continue
            if db.get(url) is None:
                db[url] = {'LAST_UPDATE': datetime.datetime.now(), 'HTMLS':[], 'DELETED':False}
            print(soup.title.text, url, datetime.datetime.now())
            obj = db[url]
            obj['HTMLS'].append({'DATE':datetime.datetime.now(), 'HTML': r.text})
            # - Update
            db[url] = obj
            db.commit()
        except Exception as ex:
            print(ex)
            continue

def run():
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

    args = [[i] for i in reversed(range(int(max_post_id) - 10000 * 5, int(max_post_id)))]
    keys = [i[0]%16 for i in args]
    df = pd.DataFrame({'arg':args, 'key':keys}).groupby(by=['key']).sum().reset_index()
    args = df.to_dict('records')
    with PPE(max_workers=16) as exe:
        exe.map(pmap, args)
