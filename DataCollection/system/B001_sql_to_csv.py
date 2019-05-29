import random
from sqlitedict import *
import pickle
import bs4
import pandas as pd
import json
from concurrent.futures import ProcessPoolExecutor as PPE



def pmap(arg):
    key, urls = arg
    db = SqliteDict('db.sqlite', encode=pickle.dumps,
                    decode=pickle.loads)
    objs = []
    random.shuffle(urls)
    db_b = SqliteDict('db_b.sqlite', encode=pickle.dumps,
                 decode=pickle.loads, autocommit=True)
    for idx, url in enumerate(urls):
        val = db[url]
        if val.get('DELETED') is None:
            continue
        if val['DELETED'] is True:
            continue
        #if db_b.get(url) is not None:
        #    continue
        HTMLS = val['HTMLS']
        soup = bs4.BeautifulSoup(HTMLS[-1]['HTML'])
        parse_date = HTMLS[-1]['DATE']
        try:
            tags = [a.text for a in soup.find('span', {'class':'tag_box'}).find_all('a', {'class':'rad_btn tag_type_1'})] 
            pub_date = soup.find('span', {'class': 'info_date'}).get('content')
            icon_view = soup.find('span', {'class': 'icon_view'}).text
            title = soup.title.text
            tweets = ' '.join(
                [t.text for t in soup.find_all('div', {'class': 'tweet'})])
            obj = {'PUB_DATE': pub_date, 'TITLE': title,
                    'TWEET': tweets, 'ICON_VIEW': icon_view, 'URL': url, 'TAGS':json.dumps(tags, ensure_ascii=False)}
            db_b[url] = obj
            print(idx, len(urls), url)
            
        except Exception as ex:
            print(ex, url)
    del db_b

def run():
    db_ = SqliteDict('db.sqlite', encode=pickle.dumps,
                     decode=pickle.loads, autocommit=True)
    args = {}
    for idx, url in enumerate(db_.keys()):
        #print(idx, url)
        key = idx % 16
        if args.get(key) is None:
            args[key] = []
        args[key].append(url)
    args = [(key, urls) for key, urls in args.items()]
    del db_
    #[pmap(arg) for arg in args]
    objs = []
    with PPE(max_workers=16) as exe:
        exe.map(pmap, args)
    db = SqliteDict('db_b.sqlite', encode=pickle.dumps,
             decode=pickle.loads)
    pd.DataFrame(list(db.values())).to_csv('local.csv', index=None)

if __name__ == '__main__':
    run()
