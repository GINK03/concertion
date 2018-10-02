
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client['news_dwango']
collection = db['collection']

for post in collection.find():
  print(post)
