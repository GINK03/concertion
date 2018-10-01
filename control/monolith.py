import json
term_index = json.load(open('../cold_start_modeling/term_index.json'))




from pymongo import MongoClient
client = MongoClient('localhost', 27017)
dbs = [ client['news_dmm_co_jp'], client['news_dwango'] ]
import MeCab 
from collections import Counter
import datetime 
m = MeCab.Tagger('-Owakati')

canonicals = []; objs = []
for db in dbs:
  collection = db['collection']
  for post in collection.find():
    try:
      time = datetime.datetime.strptime( post['date'], '%Y/%m/%d')
    except: continue
    #print(post.keys())
    delta = datetime.datetime.now() - time
    if delta.days <= 7: 
      terms = m.parse( post['title'] + post['article'] ).strip().split()
      canonicals.append( post['canonical'] )
      # 本当はここで日付指定を行う
      obj = dict(Counter(terms))
      objs.append(obj)  
      #print(obj)
horizon = len(term_index)
vertical = len(objs)
from scipy.sparse import lil_matrix
import numpy as np

lil = lil_matrix((vertical, horizon), dtype=np.float16)
for h, tf in enumerate(objs):
  #print(h)
  for term, freq in tf.items():
    if term_index.get(term) is None:
      continue
    lil[h, term_index[term]] = freq

from scipy.sparse import csr_matrix
csr  = csr_matrix(lil).astype(np.float32)

import pickle, glob
models = [ pickle.load(open(model, 'rb')) for model in glob.glob('../cold_start_modeling/models/*.pkl') ]

yp = np.vstack( [ model.predict(csr) for model in models] )
print(yp.shape)
# アンサンブルした
yp = yp.mean(axis=0)
for c,y in zip(canonicals, yp):
  print(c,y)
