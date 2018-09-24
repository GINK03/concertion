import glob
import json
import gzip
from bs4 import BeautifulSoup as BS
import shelve
import sys
from pathlib import Path
import hashlib
if '--insert' in sys.argv:
  args = {}
  for index, fn in enumerate(glob.glob('./htmls/*')):
    key = index%12
    if args.get(key) is None:
      args[key] = []
    args[key].append( fn )
  args = [(key, fns) for key, fns in args.items()]

  def pmap(arg):
    key, fns = arg
    for fn in fns:
      html = gzip.decompress( open(fn, 'rb').read() )
      soup = BS(html, 'html.parser')
      obj = {}
      try:
        t1 = ( soup.find('title').text )
        try:
          t2 = ( soup.find('span', {'class':'comment-count-title'}).text )
        except:
          Path(fn).unlink()
          continue
        t3 = (soup.find('div', {'class':'story'}).text)
        try:
          t4 = soup.find('meta', {'itemprop':'datePublished'}).get('content')
        except:
          Path(fn).unlink()
          continue
        obj[t1] = {'title':t1, 'clip':t2, 'body':t3, 'timestamp':t4}
        datum = json.dumps(obj, indent=2, ensure_ascii=False)
        hashval = hashlib.sha256(bytes(datum, 'utf8')).hexdigest()

        open(f'jsons/{hashval}', 'w').write( datum )
      except Exception as ex:
        print(ex)
        continue
  
  #for arg in args:
  #  pmap(arg)
  from concurrent.futures import ProcessPoolExecutor as PPE
  with PPE(max_workers=12) as exe:
    exe.map(pmap, args)

if '--endb' in sys.argv:
  from pathlib import Path

  with shelve.open('spam') as db:
    for p in Path('./jsons').glob('*'):
      obj = json.load(p.open())
      for k, obj2 in obj.items():
        print(obj)
        db[k] = obj2

if '--print' in sys.argv:
  with shelve.open('spam') as db:
    for key in list(db.keys()):
      print(key, db[key])
