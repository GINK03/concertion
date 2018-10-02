from pathlib import Path
from bs4 import BeautifulSoup as BS
import re

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['vipper_jp']
collection = db['collection']
for path in Path('htmls').glob('*'):
  soup = BS(path.open().read(), 'html.parser')

  title = soup.title
  if title is None:
    continue
  title = title.text

  canonical = soup.find('link', {'rel':'canonical'})
  if canonical is None:
    continue
  canonical = canonical.get('href')

  
  ul = soup.find('ul', {'class':'meta'})
  if ul is None: 
    continue
  lis = ul.find_all('li')
  
  
  if len(lis) >= 2 and '画像あり' not in lis[1].text:
    continue
  date = lis[0].text
  for rep, tar in [('Date', ''), ('年', '/'), ('月','/'), ('日', '')]:
    date = date.replace(rep, tar)
  #print(date)
  #print(title)
  article = soup.find('div', {'class':'article'})
  if article is None:
    continue
  article = re.sub(r'\s{1,}', ' ', article.text)
  obj = { 'title': title,
          'canonical':canonical,
          'date':date, 
          'article':article
        }
  print(obj)
  collection.insert_one(obj)

