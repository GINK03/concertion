import glob
import json
import gzip
from bs4 import BeautifulSoup as BS
import shelve
import sys

if '--insert' in sys.argv:
  with shelve.open('spam') as db:
    for fn in glob.glob('./htmls/*'):
      html = gzip.decompress( open(fn, 'rb').read() )

      soup = BS(html)
     
      obj = {}
      try:
        t1 = ( soup.find('title').text )
        t2 = ( soup.find('span', {'class':'textclip'}).text.strip() )
        try:
          t3 = ( soup.find('div', {'class':'page-content'}).text.strip())
        except:
          t3 = None
        try:
          t4 = ( soup.find('div', {'class':'my-slider_wrap'}).find('img', {'class':'img_photo'}).get('src') )
        except:
          t4 = None

        obj[t1] = {'title':t1, 'clip':t2, 'page-content':t3, 'img_photo':t4}
        db[t1] = {'title':t1, 'clip':t2, 'page-content':t3, 'img_photo':t4} 
        #print(obj)
      except Exception as ex:
        print(ex)
        continue

if '--print' in sys.argv:
  with shelve.open('spam') as db:
    for key in list(db.keys()):
      print(db[key])
