from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL_COMBINED")
client = MongoClient(MONGO_URL)
db = client.fashion_db

# User Style Profile Collection
user_profiles = db.user_profiles

class StyleProfile:
    """Style profile model with user style preferences"""
    def __init__(self, user_id, preferred_colors=None, preferred_styles=None, 
                 preferred_categories=None, disliked_colors=None, disliked_styles=None, 
                 occasion_preferences=None, season_preferences=None, budget_range=None):
        self.user_id = user_id
        self.preferred_colors = preferred_colors or []
        self.preferred_styles = preferred_styles or []
        self.preferred_categories = preferred_categories or []
        self.disliked_colors = disliked_colors or []
        self.disliked_styles = disliked_styles or []
        self.occasion_preferences = occasion_preferences or {}
        self.season_preferences = season_preferences or {}
        self.budget_range = budget_range or {"min": 0, "max": 1000}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "preferred_colors": self.preferred_colors,
            "preferred_styles": self.preferred_styles,
            "preferred_categories": self.preferred_categories,
            "disliked_colors": self.disliked_colors,
            "disliked_styles": self.disliked_styles,
            "occasion_preferences": self.occasion_preferences,
            "season_preferences": self.season_preferences,
            "budget_range": self.budget_range,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        profile = cls(
            user_id=data.get("user_id"),
            preferred_colors=data.get("preferred_colors", []),
            preferred_styles=data.get("preferred_styles", []),
            preferred_categories=data.get("preferred_categories", []),
            disliked_colors=data.get("disliked_colors", []),
            disliked_styles=data.get("disliked_styles", []),
            occasion_preferences=data.get("occasion_preferences", {}),
            season_preferences=data.get("season_preferences", {}),
            budget_range=data.get("budget_range", {"min": 0, "max": 1000})
        )
        profile.created_at = data.get("created_at", datetime.now())
        profile.updated_at = data.get("updated_at", datetime.now())
        return profile
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = user_profiles.find_one({"user_id": user_id})
        if data:
            return cls.from_dict(data)
        return None
    
    def save(self):
        self.updated_at = datetime.now()
        data = self.to_dict()
        
        if user_profiles.find_one({"user_id": self.user_id}):
            user_profiles.update_one({"user_id": self.user_id}, {"$set": data})
        else:
            user_profiles.insert_one(data)
        
        return self 