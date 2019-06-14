import random
import pickle
import bs4
import pandas as pd
import json
from concurrent.futures import ProcessPoolExecutor as PPE
from pathlib import Path
import datetime
from FSDB import *
Path('tmp').mkdir(exist_ok=True)

def pmap(arg):
    key, urls = arg
    objs = []
    try:
        urls = sorted(urls)[-1000:]
        #urls
        for idx, url in enumerate(urls):
            try:
                if is_deleted(url):
                    continue
                val = get(url)
                HTMLS = val['HTMLS']
                soup = bs4.BeautifulSoup(HTMLS[-1]['HTML'])
                parse_date = HTMLS[-1]['DATE']
                tags = [a.text for a in soup.find('span', {'class':'tag_box'}).find_all('a', {'class':'rad_btn tag_type_1'})] 
                pub_date = soup.find('span', {'class': 'info_date'}).get('content')
                icon_view = soup.find('span', {'class': 'icon_view'}).text
                title = soup.title.text
                tweets = ' '.join(
                    [t.text for t in soup.find_all('div', {'class': 'tweet'})])
                obj = {'PUB_DATE': pub_date, 'TITLE': title,
                        'TWEET': tweets, 'ICON_VIEW': icon_view, 'URL': url, 'TAGS':json.dumps(tags, ensure_ascii=False)}
                print(key, '@', idx, len(urls), url, tags, datetime.datetime.now())
                objs.append(obj) 
            except Exception as ex:
                print(ex, url)
    except Exception as ex:
        print(ex, key)

    return objs 

def run():
    max_post_id = get_seeds()
    urls = [f'https://togetter.com/li/{i}' for i in reversed(range(int(max_post_id) - 10000 * 5, int(max_post_id)))]
     
    args = {}
    for idx, url in enumerate(urls):
        #print(idx, url)
        key = idx % 16
        if args.get(key) is None:
            args[key] = []
        args[key].append(url)
    args = [(key, urls) for key, urls in args.items()]
    #[pmap(arg) for arg in args]
    #exit()
    objs = []
    with PPE(max_workers=8) as exe:
        for _objs in exe.map(pmap, args):
            objs += _objs

    print('finish make chunked objs, try to build local csv')
    pd.DataFrame(objs).to_csv('local.csv', index=None)

if __name__ == '__main__':
    run()
