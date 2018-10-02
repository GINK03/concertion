
import requests
from bs4 import BeautifulSoup as BS
from hashlib import sha256
import os
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

rss = 'https://gunosy.com/tags/640.rss'

soup = BS(requests.get(rss).text, 'xml')
links = [link.text for link in soup.find_all('link')]
print(links)

def build(url):
  try:
    hash_val = sha256(bytes(url, 'utf8')).hexdigest() 
    if os.path.exists(f'htmls/{hash_val}') or os.path.exists(f'dead-links/{hash_val}'): 
      return set()
    try:
      r = requests.get(url, headers=headers, timeout=10.0)
    except Exception as ex:
      print(ex)
      print('dead link')
      open(f'dead-links/{hash_val}', 'w').write( str(ex) )
      return set()

    soup = BS(r.text, 'html.parser')
    html = r.text
    open(f'htmls/{hash_val}', 'w').write( html )
    hrefs = set()
    for a in soup.find_all('a', {'href':True}):
      href = a.get('href')
      if href[0] == '/' and len(href) > 1:
        href = seed[:-1] + href
      hrefs.add(href)
    return hrefs
  except Exception as ex:
    print(ex)
    return set()

hrefs = set()
from concurrent.futures import ThreadPoolExecutor as PPE
with PPE(max_workers=10) as exe:
  for _hrefs in exe.map(build, links):
    hrefs |= _hrefs
args = hrefs 
