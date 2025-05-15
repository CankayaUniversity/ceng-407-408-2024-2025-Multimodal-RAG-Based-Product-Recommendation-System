from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL_COMBINED")
client = MongoClient(MONGO_URL)
db = client.fashion_db

# User Photos Collection
user_photos = db.user_photos

class UserPhoto:
    """Model for user profile photos"""
    def __init__(self, user_id, photo_data, content_type):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.photo_data = photo_data  # Base64 encoded image data
        self.content_type = content_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "photo_data": self.photo_data,
            "content_type": self.content_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        photo = cls(
            user_id=data.get("user_id"),
            photo_data=data.get("photo_data"),
            content_type=data.get("content_type")
        )
        photo.id = data.get("_id")
        photo.created_at = data.get("created_at", datetime.now())
        photo.updated_at = data.get("updated_at", datetime.now())
        return photo
    
    def save(self):
        self.updated_at = datetime.now()
        if user_photos.find_one({"_id": self.id}):
            user_photos.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            user_photos.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = user_photos.find_one({"user_id": user_id})
        if data:
            return cls.from_dict(data)
        return None 