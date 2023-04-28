import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class DBMS:

  def __init__(self):
    self.client = MongoClient(os.environ['MONGO'],
                                      server_api=ServerApi('1'))
    self.db = self.client.projects
    self.collection = self.db.w3schools2
    self.collection.delete_many({})

  def insert_data(self, data):
    self.collection.insert_one(data)

  def get_data(self, url_path):
    return self.collection.find_one({'url': url_path})

  def update_data(self, url_path, data):
    self.collection.update_one({'url': url_path}, {'$set': data})
