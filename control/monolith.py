import json
term_index = json.load(open('../cold_start_modeling/term_index.json'))




from pymongo import MongoClient
client = MongoClient('localhost', 27017)
dbs = [ client['news_dmm_co_jp'], client['news_dwango'] ]
import MeCab 
from collections import Counter
import datetime 
m = MeCab.Tagger('-Owakati')
for db in dbs:
  collection = db['collection']
  for post in collection.find():
    try:
      time = datetime.datetime.strptime( post['date'], '%Y/%m/%d')
    except: continue
    print(post.keys())
    delta = datetime.datetime.now() - time
    if delta.days <= 7: 
      terms = m.parse( post['title'] + post['article'] ).strip().split()
      # 本当はここで日付指定を行う
      obj = dict(Counter(terms))
      print(obj)
