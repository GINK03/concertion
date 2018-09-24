import glob
import shelve
import MeCab
from collections import Counter
import pickle
import sys
import json
if '--wakati' in sys.argv:
  db = shelve.open('../cold_start_dataset2/spam')
  m = MeCab.Tagger('-Owakati')
  tfs = []
  for key in list(db.keys()):
    obj = db[key]

    try:
      page = obj['title'] + obj['body']
    except: 
      print(list(obj.keys()))
      continue
    #print(page)
    body = m.parse(page).split()
    tf = dict(Counter(body))
    tfs.append(tf)
  pickle.dump(tfs, open('tfs.pkl', 'wb'))


if '--term_index' in sys.argv:
  tfs = pickle.load(open('tfs.pkl', 'rb'))
  term_index = {}
  for tf in tfs:
    for key in tf.keys():
      if term_index.get(key) is None:
        term_index[key] = len(term_index)
  json.dump(term_index, fp=open('term_index.json', 'w'), indent=2, ensure_ascii=False)
