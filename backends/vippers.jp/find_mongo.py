
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client['vipper_jp']
collection = db['collection']

for post in collection.find():
  print(post)
