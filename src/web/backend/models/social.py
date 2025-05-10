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

# Social features collections
posts = db.posts
comments = db.comments
likes = db.likes
outfit_challenges = db.outfit_challenges
challenge_entries = db.challenge_entries
stylist_consultations = db.stylist_consultations
follow_relationships = db.follow_relationships

class Post:
    """User post model for the style community"""
    def __init__(self, user_id, content=None, title=None, image_urls=None, 
                 outfit_items=None, tags=None, visibility="public"):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.content = content or ""
        self.title = title or ""
        self.image_urls = image_urls or []
        self.outfit_items = outfit_items or []  # References to wardrobe items or products
        self.tags = tags or []
        self.visibility = visibility  # public, private, followers
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.like_count = 0
        self.comment_count = 0
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "title": self.title,
            "image_urls": self.image_urls,
            "outfit_items": self.outfit_items,
            "tags": self.tags,
            "visibility": self.visibility,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "like_count": self.like_count,
            "comment_count": self.comment_count
        }
    
    @classmethod
    def from_dict(cls, data):
        post = cls(
            user_id=data.get("user_id"),
            content=data.get("content"),
            title=data.get("title"),
            image_urls=data.get("image_urls"),
            outfit_items=data.get("outfit_items"),
            tags=data.get("tags"),
            visibility=data.get("visibility")
        )
        post.id = data.get("_id")
        post.created_at = data.get("created_at", datetime.now())
        post.updated_at = data.get("updated_at", datetime.now())
        post.like_count = data.get("like_count", 0)
        post.comment_count = data.get("comment_count", 0)
        return post
    
    def save(self):
        self.updated_at = datetime.now()
        if posts.find_one({"_id": self.id}):
            posts.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            posts.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_by_id(cls, post_id):
        data = posts.find_one({"_id": post_id})
        if data:
            return cls.from_dict(data)
        return None
    
    @classmethod
    def get_feed(cls, user_id, limit=20, offset=0, include_following_only=False):
        """Get a feed of posts for a user - can be filtered to following only"""
        if include_following_only:
            following_ids = [f["followed_id"] for f in 
                             follow_relationships.find({"follower_id": user_id})]
            query = {"user_id": {"$in": following_ids}, "visibility": {"$ne": "private"}}
        else:
            query = {"visibility": "public"}
            
        cursor = posts.find(query).sort("created_at", -1).skip(offset).limit(limit)
        return [cls.from_dict(post) for post in cursor]
    
    @classmethod
    def get_user_posts(cls, user_id, limit=20, offset=0):
        """Get posts by a specific user"""
        cursor = posts.find({"user_id": user_id}).sort("created_at", -1).skip(offset).limit(limit)
        return [cls.from_dict(post) for post in cursor]
    
    def increment_like_count(self):
        posts.update_one({"_id": self.id}, {"$inc": {"like_count": 1}})
        self.like_count += 1
        return self
    
    def decrement_like_count(self):
        if self.like_count > 0:
            posts.update_one({"_id": self.id}, {"$inc": {"like_count": -1}})
            self.like_count -= 1
        return self
    
    def increment_comment_count(self):
        posts.update_one({"_id": self.id}, {"$inc": {"comment_count": 1}})
        self.comment_count += 1
        return self
    
    def delete(self):
        # Delete comments and likes when post is deleted
        comments.delete_many({"post_id": self.id})
        likes.delete_many({"post_id": self.id})
        posts.delete_one({"_id": self.id})

class Comment:
    """Comment model for posts"""
    def __init__(self, user_id, post_id, content):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
        self.created_at = datetime.now()
        self.like_count = 0
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "content": self.content,
            "created_at": self.created_at,
            "like_count": self.like_count
        }
    
    @classmethod
    def from_dict(cls, data):
        comment = cls(
            user_id=data.get("user_id"),
            post_id=data.get("post_id"),
            content=data.get("content")
        )
        comment.id = data.get("_id")
        comment.created_at = data.get("created_at", datetime.now())
        comment.like_count = data.get("like_count", 0)
        return comment
    
    def save(self):
        # Increment comment count on the post
        post = Post.get_by_id(self.post_id)
        if post:
            post.increment_comment_count()
            
        comments.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_post_comments(cls, post_id, limit=50, offset=0):
        cursor = comments.find({"post_id": post_id}).sort("created_at", 1).skip(offset).limit(limit)
        return [cls.from_dict(comment) for comment in cursor]
    
    def increment_like_count(self):
        comments.update_one({"_id": self.id}, {"$inc": {"like_count": 1}})
        self.like_count += 1
        return self
    
    def delete(self):
        # Decrement comment count on the post
        post = Post.get_by_id(self.post_id)
        if post:
            post.decrement_comment_count()
            
        comments.delete_one({"_id": self.id})

class Like:
    """Like model for posts and comments"""
    def __init__(self, user_id, target_id, target_type):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.target_id = target_id
        self.target_type = target_type  # post or comment
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        like = cls(
            user_id=data.get("user_id"),
            target_id=data.get("target_id"),
            target_type=data.get("target_type")
        )
        like.id = data.get("_id")
        like.created_at = data.get("created_at", datetime.now())
        return like
    
    def save(self):
        # Check if already liked
        existing = likes.find_one({
            "user_id": self.user_id,
            "target_id": self.target_id,
            "target_type": self.target_type
        })
        
        if existing:
            return self
        
        # Increment like count on the target
        if self.target_type == "post":
            post = Post.get_by_id(self.target_id)
            if post:
                post.increment_like_count()
        elif self.target_type == "comment":
            # Increment like count on the comment
            comments.update_one({"_id": self.target_id}, {"$inc": {"like_count": 1}})
            
        likes.insert_one(self.to_dict())
        return self
    
    @classmethod
    def user_has_liked(cls, user_id, target_id, target_type):
        return likes.find_one({
            "user_id": user_id,
            "target_id": target_id,
            "target_type": target_type
        }) is not None
    
    def delete(self):
        # Decrement like count on the target
        if self.target_type == "post":
            post = Post.get_by_id(self.target_id)
            if post:
                post.decrement_like_count()
        elif self.target_type == "comment":
            # Decrement like count on the comment
            comments.update_one({"_id": self.target_id}, {"$inc": {"like_count": -1}})
            
        likes.delete_one({"_id": self.id})

class OutfitChallenge:
    """Outfit challenge model for community challenges"""
    def __init__(self, title, description, theme, start_date, end_date, 
                 image_url=None, created_by=None, rules=None, prizes=None):
        self.id = str(ObjectId())
        self.title = title
        self.description = description
        self.theme = theme
        self.start_date = start_date
        self.end_date = end_date
        self.image_url = image_url
        self.created_by = created_by  # Admin or user who created the challenge
        self.rules = rules or []
        self.prizes = prizes or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.entry_count = 0
        self.status = "upcoming"  # upcoming, active, voting, completed
    
    def to_dict(self):
        return {
            "_id": self.id,
            "title": self.title,
            "description": self.description,
            "theme": self.theme,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "image_url": self.image_url,
            "created_by": self.created_by,
            "rules": self.rules,
            "prizes": self.prizes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "entry_count": self.entry_count,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        challenge = cls(
            title=data.get("title"),
            description=data.get("description"),
            theme=data.get("theme"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            image_url=data.get("image_url"),
            created_by=data.get("created_by"),
            rules=data.get("rules"),
            prizes=data.get("prizes")
        )
        challenge.id = data.get("_id")
        challenge.created_at = data.get("created_at", datetime.now())
        challenge.updated_at = data.get("updated_at", datetime.now())
        challenge.entry_count = data.get("entry_count", 0)
        challenge.status = data.get("status", "upcoming")
        return challenge
    
    def save(self):
        self.updated_at = datetime.now()
        
        # Update status based on dates
        now = datetime.now()
        if now < self.start_date:
            self.status = "upcoming"
        elif now > self.end_date:
            self.status = "completed"
        else:
            self.status = "active"
            
        if outfit_challenges.find_one({"_id": self.id}):
            outfit_challenges.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            outfit_challenges.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_by_id(cls, challenge_id):
        data = outfit_challenges.find_one({"_id": challenge_id})
        if data:
            return cls.from_dict(data)
        return None
    
    @classmethod
    def get_active_challenges(cls, limit=10, offset=0):
        now = datetime.now()
        query = {
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        }
        cursor = outfit_challenges.find(query).sort("end_date", 1).skip(offset).limit(limit)
        return [cls.from_dict(challenge) for challenge in cursor]
    
    @classmethod
    def get_upcoming_challenges(cls, limit=10, offset=0):
        now = datetime.now()
        query = {"start_date": {"$gt": now}}
        cursor = outfit_challenges.find(query).sort("start_date", 1).skip(offset).limit(limit)
        return [cls.from_dict(challenge) for challenge in cursor]
    
    @classmethod
    def get_completed_challenges(cls, limit=10, offset=0):
        now = datetime.now()
        query = {"end_date": {"$lt": now}}
        cursor = outfit_challenges.find(query).sort("end_date", -1).skip(offset).limit(limit)
        return [cls.from_dict(challenge) for challenge in cursor]
    
    def increment_entry_count(self):
        outfit_challenges.update_one({"_id": self.id}, {"$inc": {"entry_count": 1}})
        self.entry_count += 1
        return self

class ChallengeEntry:
    """Entry for an outfit challenge"""
    def __init__(self, challenge_id, user_id, title, description, image_urls, 
                 outfit_items=None):
        self.id = str(ObjectId())
        self.challenge_id = challenge_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.image_urls = image_urls or []
        self.outfit_items = outfit_items or []  # References to wardrobe items or products
        self.created_at = datetime.now()
        self.vote_count = 0
    
    def to_dict(self):
        return {
            "_id": self.id,
            "challenge_id": self.challenge_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "image_urls": self.image_urls,
            "outfit_items": self.outfit_items,
            "created_at": self.created_at,
            "vote_count": self.vote_count
        }
    
    @classmethod
    def from_dict(cls, data):
        entry = cls(
            challenge_id=data.get("challenge_id"),
            user_id=data.get("user_id"),
            title=data.get("title"),
            description=data.get("description"),
            image_urls=data.get("image_urls"),
            outfit_items=data.get("outfit_items")
        )
        entry.id = data.get("_id")
        entry.created_at = data.get("created_at", datetime.now())
        entry.vote_count = data.get("vote_count", 0)
        return entry
    
    def save(self):
        # Increment entry count on the challenge
        challenge = OutfitChallenge.get_by_id(self.challenge_id)
        if challenge:
            challenge.increment_entry_count()
            
        if challenge_entries.find_one({"_id": self.id}):
            challenge_entries.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            challenge_entries.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_challenge_entries(cls, challenge_id, limit=50, offset=0, sort_by="created_at"):
        """Get entries for a specific challenge"""
        sort_order = -1 if sort_by == "vote_count" else 1  # Descending for votes, ascending for time
        cursor = challenge_entries.find({"challenge_id": challenge_id}).sort(sort_by, sort_order).skip(offset).limit(limit)
        return [cls.from_dict(entry) for entry in cursor]
    
    @classmethod
    def get_user_entries(cls, user_id, limit=20, offset=0):
        """Get all entries by a specific user"""
        cursor = challenge_entries.find({"user_id": user_id}).sort("created_at", -1).skip(offset).limit(limit)
        return [cls.from_dict(entry) for entry in cursor]
    
    def increment_vote_count(self):
        challenge_entries.update_one({"_id": self.id}, {"$inc": {"vote_count": 1}})
        self.vote_count += 1
        return self

class StylistConsultation:
    """Model for AI Stylist Consultations"""
    def __init__(self, user_id, date, status="scheduled", focus_areas=None, 
                 questions=None, style_preferences=None, consultation_type="ai"):
        self.id = str(ObjectId())
        self.user_id = user_id
        self.date = date
        self.status = status  # scheduled, completed, cancelled
        self.focus_areas = focus_areas or []  # e.g., "seasonal wardrobe", "special event"
        self.questions = questions or []
        self.style_preferences = style_preferences or {}
        self.consultation_type = consultation_type  # ai or human
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.notes = []
        self.recommendations = []
    
    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "status": self.status,
            "focus_areas": self.focus_areas,
            "questions": self.questions,
            "style_preferences": self.style_preferences,
            "consultation_type": self.consultation_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
            "recommendations": self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data):
        consultation = cls(
            user_id=data.get("user_id"),
            date=data.get("date"),
            status=data.get("status", "scheduled"),
            focus_areas=data.get("focus_areas"),
            questions=data.get("questions"),
            style_preferences=data.get("style_preferences"),
            consultation_type=data.get("consultation_type", "ai")
        )
        consultation.id = data.get("_id")
        consultation.created_at = data.get("created_at", datetime.now())
        consultation.updated_at = data.get("updated_at", datetime.now())
        consultation.notes = data.get("notes", [])
        consultation.recommendations = data.get("recommendations", [])
        return consultation
    
    def save(self):
        self.updated_at = datetime.now()
        if stylist_consultations.find_one({"_id": self.id}):
            stylist_consultations.update_one({"_id": self.id}, {"$set": self.to_dict()})
        else:
            stylist_consultations.insert_one(self.to_dict())
        return self
    
    @classmethod
    def get_by_id(cls, consultation_id):
        data = stylist_consultations.find_one({"_id": consultation_id})
        if data:
            return cls.from_dict(data)
        return None
    
    @classmethod
    def get_user_consultations(cls, user_id, limit=20, offset=0):
        cursor = stylist_consultations.find({"user_id": user_id}).sort("date", -1).skip(offset).limit(limit)
        return [cls.from_dict(consultation) for consultation in cursor]
    
    def add_note(self, note):
        """Add a note to the consultation"""
        note_obj = {
            "text": note,
            "timestamp": datetime.now()
        }
        self.notes.append(note_obj)
        stylist_consultations.update_one(
            {"_id": self.id}, 
            {"$push": {"notes": note_obj}}
        )
        return self
    
    def add_recommendation(self, product_id, product_name, reason, image_url=None):
        """Add a product recommendation to the consultation"""
        rec_obj = {
            "product_id": product_id,
            "product_name": product_name,
            "reason": reason,
            "image_url": image_url,
            "timestamp": datetime.now()
        }
        self.recommendations.append(rec_obj)
        stylist_consultations.update_one(
            {"_id": self.id}, 
            {"$push": {"recommendations": rec_obj}}
        )
        return self

class FollowRelationship:
    """Model for user follow relationships"""
    def __init__(self, follower_id, followed_id):
        self.id = str(ObjectId())
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            "_id": self.id,
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        relationship = cls(
            follower_id=data.get("follower_id"),
            followed_id=data.get("followed_id")
        )
        relationship.id = data.get("_id")
        relationship.created_at = data.get("created_at", datetime.now())
        return relationship
    
    def save(self):
        # Check if already following
        existing = follow_relationships.find_one({
            "follower_id": self.follower_id,
            "followed_id": self.followed_id
        })
        
        if not existing:
            follow_relationships.insert_one(self.to_dict())
        return self
    
    @classmethod
    def is_following(cls, follower_id, followed_id):
        return follow_relationships.find_one({
            "follower_id": follower_id,
            "followed_id": followed_id
        }) is not None
    
    @classmethod
    def get_followers(cls, user_id, limit=50, offset=0):
        """Get users who follow the specified user"""
        cursor = follow_relationships.find({"followed_id": user_id}).skip(offset).limit(limit)
        return [rel["follower_id"] for rel in cursor]
    
    @classmethod
    def get_following(cls, user_id, limit=50, offset=0):
        """Get users that the specified user follows"""
        cursor = follow_relationships.find({"follower_id": user_id}).skip(offset).limit(limit)
        return [rel["followed_id"] for rel in cursor]
    
    @classmethod
    def get_follower_count(cls, user_id):
        return follow_relationships.count_documents({"followed_id": user_id})
    
    @classmethod
    def get_following_count(cls, user_id):
        return follow_relationships.count_documents({"follower_id": user_id})
    
    def delete(self):
        follow_relationships.delete_one({
            "follower_id": self.follower_id,
            "followed_id": self.followed_id
        }) 