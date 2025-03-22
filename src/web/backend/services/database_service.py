from pymongo import MongoClient
from lib import Singleton
import os


class DatabaseService(metaclass=Singleton):

    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGO_URL"),
            username=os.getenv("MONGO_USERNAME"),
            password=os.getenv("MONGO_PASSWORD"),
        )
        self.database = self.client.get_database(os.getenv("MONGO_DB_NAME"))
    
    def get_collection(self, collection_name:str):
        return self.database.get_collection(collection_name)
