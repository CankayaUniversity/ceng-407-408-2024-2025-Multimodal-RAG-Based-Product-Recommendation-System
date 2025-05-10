import os
from pymongo import MongoClient
from dotenv import load_dotenv
from lib.singleton import Singleton

load_dotenv()

class DatabaseService(metaclass=Singleton):

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URL_COMBINED"))
        self.database = self.client.get_database(os.getenv("MONGO_DB_NAME"))

    def get_collection(self, collection_name:str):
        return self.database.get_collection(collection_name)
