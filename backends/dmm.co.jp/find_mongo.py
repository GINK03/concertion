
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client['news_dmm_co_jp']
collection = db['collection']

for post in collection.find():
  print(post)
