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

# Collections
users = db.users
user_photos = db.user_photos
style_profiles = db.style_profiles

class UserProfile:
    """User profile model"""
    def __init__(self, user_id, username=None, email=None, full_name=None, 
                 bio=None, profile_image=None, preferences=None):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.bio = bio
        self.profile_image = profile_image
        self.preferences = preferences or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "bio": self.bio,
            "profile_image": self.profile_image,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        profile = cls(
            user_id=data.get("user_id"),
            username=data.get("username"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            bio=data.get("bio"),
            profile_image=data.get("profile_image"),
            preferences=data.get("preferences")
        )
        profile.id = data.get("_id")
        profile.created_at = data.get("created_at", datetime.now())
        profile.updated_at = data.get("updated_at", datetime.now())
        return profile
    
    def save(self):
        self.updated_at = datetime.now()
        if users.find_one({"_id": self.id}):
            users.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            users.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_by_id(cls, profile_id):
        data = users.find_one({"_id": profile_id})
        if data:
            return cls.from_dict(data)
        return None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = users.find_one({"user_id": user_id})
        if data:
            return cls.from_dict(data)
        return None
    
    def update_preferences(self, preferences):
        self.preferences.update(preferences)
        self.save()
        return self 