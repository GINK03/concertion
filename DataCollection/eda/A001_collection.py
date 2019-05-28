import requests
import bs4
import json
import pickle
from sqlitedict import *
import datetime
from concurrent.futures import ProcessPoolExecutor as PPE
import itertools
import pandas as pd
'''
TABLE DEFINITIONS
{
    'LAST_UPDATE': datetime,
    'HTMLS': [{'DATE':datetime, 'HTML':html }],
    'DELETED':boolean,
}
'''

args = [[i] for i in reversed(range(1200000, 1360507))]
keys = [i[0]%16 for i in args]
df = pd.DataFrame({'arg':args, 'key':keys}).groupby(by=['key']).sum().reset_index()
args = df.to_dict('records')
def pmap(arg):
    ii = arg['arg']
    db = SqliteDict('db.sqlite', encode=pickle.dumps, decode=pickle.loads, autocommit=True)
    for i in ii:
        url = f'https://togetter.com/li/{i}'
        if db.get(url) is not None:
            continue
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text)
        if soup.find('div', {'class':'alert alert-info'}) is not None:
            db[url] = {'DELETED':True}
            continue
        if db.get(url) is None:
            db[url] = {'LAST_UPDATE': datetime.datetime.now(), 'HTMLS':[], 'DELETED':False}
        print(soup.title.text, url)
        obj = db[url]
        obj['HTMLS'].append({'DATE':datetime.datetime.now(), 'HTML': r.text})
        # update
        db[url] = obj
        db.commit()

with PPE(max_workers=16) as exe:
    exe.map(pmap, args)
