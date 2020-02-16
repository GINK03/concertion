import random
import pickle
import bs4
import pandas as pd
import json
from concurrent.futures import ProcessPoolExecutor as PPE
from pathlib import Path
import datetime
from tqdm import tqdm
from FSDB import *

HERE = Path(__file__).resolve().parent
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent

Path(f'{TOP_FOLDER}/var/TB').mkdir(exist_ok=True)

def pmap(arg):
    key, urls = arg
    objs = []
    try:
        urls = sorted(urls)
        #urls
        for idx, url in enumerate(urls):
            try:
                if is_deleted(url):
                    continue
                val = get(url)
                if val is None:
                    continue
                HTMLS = val['HTMLS']
                soup = bs4.BeautifulSoup(HTMLS[-1]['HTML'], 'lxml')
                parse_date = HTMLS[-1]['DATE']
                tags = [a.text for a in soup.find('span', {'class':'tag_box'}).find_all('a', {'class':'rad_btn tag_type_1'})] 
                pub_date = soup.find('span', {'class': 'info_date'}).get('content')
                icon_view = soup.find('span', {'class': 'icon_view'}).text
                title = soup.title.text
                tweets = ' '.join(
                    [t.text for t in soup.find_all('div', {'class': 'tweet'})])
                obj = {'PUB_DATE': pub_date, 'TITLE': title,
                        'TWEET': tweets, 'ICON_VIEW': icon_view, 'URL': url, 'TAGS':json.dumps(tags, ensure_ascii=False)}
                #print(key, '@', idx, len(urls), url, tags, datetime.datetime.now())
                objs.append(obj) 
            except AttributeError as exc:
                # 対応していないhtmlのときなにもしない
                delete(url)
                continue
            except Exception as exc:
                # ファイルの破損が考えられるので削除する
                print(exc, url)
    except Exception as exc:
        print(exc, key)

    return objs 

def run():
    max_post_id = get_seeds()
    urls = [f'https://togetter.com/li/{i}' for i in reversed(range(int(max_post_id) - 10000 * 20, int(max_post_id)))]
     
    args = {}
    for idx, url in enumerate(urls):
        #print(idx, url)
        key = idx % 1000
        if args.get(key) is None:
            args[key] = []
        args[key].append(url)
    args = [(key, urls) for key, urls in args.items()]
    #[pmap(arg) for arg in args]
    #exit()
    objs = []
    with PPE(max_workers=8) as exe:
        for _objs in tqdm(exe.map(pmap, args), total=len(args)):
            objs += _objs

    print('finish make chunked objs, try to build local csv')
    df = pd.DataFrame(objs)
    out_folder = f'{TOP_FOLDER}/var/TB/daily_ranking' 
    Path(out_folder).mkdir(exist_ok=True, parents=True)
    for pub_date, sub in df.groupby(by=['PUB_DATE']):
        sub = sub.copy().sort_values(by=['ICON_VIEW'], ascending=False)
        sub.to_csv(f'{out_folder}/{pub_date}', index=None)

if __name__ == '__main__':
    run()
