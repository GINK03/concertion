import shelve

db = shelve.open('../cold_start_dataset/spam')

targets = []
for key in list(db.keys()):
  obj = db[key]
  try:
    num = int(obj['clip'])
  except Exception as ex:
    print(ex)
    num = 100
  targets.append(num)

import pandas as pd

df = pd.DataFrame({'target':targets})

df.to_csv('target.csv', index=None)
