from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)10s- %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Client:
    def __init__(self):
        self.client = MongoClient('mongodb://root:root@localhost:27017/')
        self.hakaton_db = self.client.hakaton_db

    def write_one_to_hakaton_db(self, collection,  data):
        self.hakaton_db[collection].insert_one(data)

    def get_data(self, collection):
        data = self.hakaton_db[collection].find()
        results = []
        for document in data:
            document['_id'] = str(document['_id'])
            results.append(document)
        return results

    def update_state(self, chat_id, data):
        self.hakaton_db['chat'].replace_one(
            {"chat_id": chat_id},
            data,
            upsert=True
        )

    def get_state(self, chat_id):
        chat = self.hakaton_db['chat'].find_one(
            {"chat_id": chat_id},
        )
        if chat:
            chat.pop('_id')
            return chat
        return {"chat_id": chat_id}
