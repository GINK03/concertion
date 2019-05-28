from sqlitedict import *
import pickle
import bs4
import pandas as pd

db = SqliteDict('db.sqlite', encode=pickle.dumps,
                decode=pickle.loads, autocommit=True)

objs = []
for idx, (key, val) in enumerate(db.iteritems()):
    if idx > 1000:
        break
    if val.get('DELETED') is None:
        del db[key]
        continue
    if val['DELETED'] is True:
        continue
    
    print(idx, key)
    HTMLS = val['HTMLS']
    soup = bs4.BeautifulSoup(HTMLS[-1]['HTML'])
    parse_date = HTMLS[-1]['DATE']

    try:
        pub_date = soup.find('span', {'class':'info_date'}).get('content')
        icon_view = soup.find('span', {'class':'icon_view'}).text
        title = soup.title.text
        tweets = ' '.join([t.text for t in soup.find_all('div', {'class':'tweet'})])
        obj = {'PUB_DATE':pub_date, 'TITLE':title, 'TWEET':tweets, 'ICON_VIEW':icon_view, 'URL':key}
        objs.append(obj)
    except Exception as ex:
        print(ex, key)

pd.DataFrame(objs).to_csv('local.csv', index=None)
