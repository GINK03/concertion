from scipy.sparse import lil_matrix

import pickle
import json
import numpy as np

term_index = json.load(open('./term_index.json'))
tfs        = pickle.load(open('./tfs.pkl', 'rb'))

for term, index in sorted(term_index.items(), key=lambda x:x[1])[:10]:
  print(term, index)
print(len(tfs), len(term_index))

lil = lil_matrix((48444, 300054), dtype=np.float16)

for h, tf in enumerate(tfs):
  print(h)
  for term, freq in tf.items():
    lil[h, term_index[term]] = freq

pickle.dump(lil, open('lil.pkl', 'wb'))
