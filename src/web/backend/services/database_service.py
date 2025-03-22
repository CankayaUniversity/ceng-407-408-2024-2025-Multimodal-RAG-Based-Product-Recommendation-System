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
    
    def get_collection(self, db_name: str, collection_name:str):
        db = self.client.get_database(db_name)
        return db.get_collection(collection_name)
