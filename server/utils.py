from pymongo import MongoClient


class Client:
    def __init__(self):
        self.client = MongoClient('mongodb://root:root@localhost:27017/')
        self.hakaton_db = self.client.hakaton_db

    def write_to_hakaton_db(self, collection,  data):
        self.hakaton_db[collection].insert_many(data)

    def get_data(self):
        pass
