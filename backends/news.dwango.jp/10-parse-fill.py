from pathlib import Path
from bs4 import BeautifulSoup as BS
import re

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['news_dwango']
collection = db['collection']
for path in Path('./htmls').glob('*'):
  soup = BS(path.open().read())

  title = soup.title
  if title is None:
    continue
  title = title.text

  canonical = soup.find('link', {'rel':'canonical'})
  if canonical is None:
    continue
  canonical = canonical.get('href')


  date = soup.find('span', {'class':'publish-date'})
  date = date.text

  article = soup.find('article')
  article = re.sub(r'\s{1,}', ' ', article.text)
  obj = { 'title': title,
          'canonical':canonical,
          'date':date, 
          'article':article
        }
  print(obj)
  #collection.insert_one(obj)
