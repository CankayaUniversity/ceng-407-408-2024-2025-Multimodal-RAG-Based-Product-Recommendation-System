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

# User Style Profile Collection
user_profiles = db.user_profiles

# User Interaction History Collection
user_interactions = db.user_interactions

# User Wardrobe Collection
user_wardrobes = db.user_wardrobes

# User Body Measurements Collection
body_measurements = db.body_measurements

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

class UserInteraction:
    """User interaction model for tracking product interactions"""
    def __init__(self, user_id, product_id, interaction_type, category=None, 
                 product_data=None, timestamp=None):
        self.user_id = user_id
        self.product_id = product_id
        self.interaction_type = interaction_type  # view, like, purchase, add_to_cart, try_on
        self.category = category
        self.product_data = product_data or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "interaction_type": self.interaction_type,
            "category": self.category,
            "product_data": self.product_data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id"),
            product_id=data.get("product_id"),
            interaction_type=data.get("interaction_type"),
            category=data.get("category"),
            product_data=data.get("product_data", {}),
            timestamp=data.get("timestamp", datetime.now())
        )
    
    def save(self):
        user_interactions.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_user_interactions(cls, user_id, limit=100, interaction_type=None):
        query = {"user_id": user_id}
        if interaction_type:
            query["interaction_type"] = interaction_type
            
        cursor = user_interactions.find(query).sort("timestamp", -1).limit(limit)
        return [cls.from_dict(item) for item in cursor]

class WardrobeItem:
    """User wardrobe item model"""
    def __init__(self, user_id, product_id=None, category=None, color=None, 
                 style=None, season=None, occasions=None, image_url=None, 
                 product_name=None, custom_name=None, purchased_date=None):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.product_id = product_id
        self.category = category
        self.color = color
        self.style = style
        self.season = season or []
        self.occasions = occasions or []
        self.image_url = image_url
        self.product_name = product_name
        self.custom_name = custom_name
        self.purchased_date = purchased_date or datetime.now()
        self.added_at = datetime.now()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "category": self.category,
            "color": self.color,
            "style": self.style,
            "season": self.season,
            "occasions": self.occasions,
            "image_url": self.image_url,
            "product_name": self.product_name,
            "custom_name": self.custom_name,
            "purchased_date": self.purchased_date,
            "added_at": self.added_at
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(
            user_id=data.get("user_id"),
            product_id=data.get("product_id"),
            category=data.get("category"),
            color=data.get("color"),
            style=data.get("style"),
            season=data.get("season"),
            occasions=data.get("occasions"),
            image_url=data.get("image_url"),
            product_name=data.get("product_name"),
            custom_name=data.get("custom_name"),
            purchased_date=data.get("purchased_date")
        )
        item.id = data.get("_id")
        item.added_at = data.get("added_at", datetime.now())
        return item
    
    def save(self):
        user_wardrobes.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_user_wardrobe(cls, user_id):
        cursor = user_wardrobes.find({"user_id": user_id})
        return [cls.from_dict(item) for item in cursor]
    
    @classmethod
    def get_by_id(cls, item_id):
        data = user_wardrobes.find_one({"_id": item_id})
        if data:
            return cls.from_dict(data)
        return None

class BodyMeasurements:
    """User body measurements model"""
    def __init__(self, user_id, height=None, weight=None, chest=None, waist=None, 
                 hips=None, inseam=None, shoulders=None, sleeve_length=None, 
                 neck=None, body_shape=None, fit_preference=None):
        self.user_id = user_id
        self.height = height  # in cm
        self.weight = weight  # in kg
        self.chest = chest    # in cm
        self.waist = waist    # in cm
        self.hips = hips      # in cm
        self.inseam = inseam  # in cm
        self.shoulders = shoulders  # in cm
        self.sleeve_length = sleeve_length  # in cm
        self.neck = neck      # in cm
        self.body_shape = body_shape  # hourglass, pear, apple, rectangle, inverted triangle
        self.fit_preference = fit_preference  # slim, regular, loose
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "height": self.height,
            "weight": self.weight,
            "chest": self.chest,
            "waist": self.waist,
            "hips": self.hips,
            "inseam": self.inseam,
            "shoulders": self.shoulders,
            "sleeve_length": self.sleeve_length,
            "neck": self.neck,
            "body_shape": self.body_shape,
            "fit_preference": self.fit_preference,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        measurements = cls(
            user_id=data.get("user_id"),
            height=data.get("height"),
            weight=data.get("weight"),
            chest=data.get("chest"),
            waist=data.get("waist"),
            hips=data.get("hips"),
            inseam=data.get("inseam"),
            shoulders=data.get("shoulders"),
            sleeve_length=data.get("sleeve_length"),
            neck=data.get("neck"),
            body_shape=data.get("body_shape"),
            fit_preference=data.get("fit_preference")
        )
        measurements.created_at = data.get("created_at", datetime.now())
        measurements.updated_at = data.get("updated_at", datetime.now())
        return measurements
    
    @classmethod
    def get_by_user_id(cls, user_id):
        data = body_measurements.find_one({"user_id": user_id})
        if data:
            return cls.from_dict(data)
        return None
    
    def save(self):
        self.updated_at = datetime.now()
        data = self.to_dict()
        
        if body_measurements.find_one({"user_id": self.user_id}):
            body_measurements.update_one({"user_id": self.user_id}, {"$set": data})
        else:
            body_measurements.insert_one(data)
        
        return self 