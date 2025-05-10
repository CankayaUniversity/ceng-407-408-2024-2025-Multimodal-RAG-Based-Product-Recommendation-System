from flask import Blueprint, jsonify
from pymongo import MongoClient
from utils.Classes.TrendFetcher import TrendFetcher
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('trends_api')

trends_bp = Blueprint("trends", __name__)
api_blueprint = Blueprint("api", __name__)  # For backward compatibility

def get_mongo_client():
    """Get a MongoDB client"""
    try:
        mongo_url = os.getenv("MONGO_URL_COMBINED")
        logger.info(f"Connecting to MongoDB at {mongo_url[:20]}...")
        return MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return None

@trends_bp.route("/trends", methods=["GET"])
def get_trends():
    """Get the latest fashion trends from MongoDB or fetch directly"""
    logger.info("Trends API endpoint called")
    
    try:
        # Try to get from MongoDB first
        client = get_mongo_client()
        if client:
            try:
                logger.info("Attempting to retrieve trends from MongoDB")
                db = client.get_database("trends_db")
                trends_collection = db.get_collection("trends")
                
                # Check if we need to refresh the cache
                latest = trends_collection.find_one(sort=[("timestamp", -1)])
                now = datetime.utcnow()
                
                if not latest or (now - latest["timestamp"] > timedelta(hours=24)):
                    logger.info("Refreshing trends cache")
                    # Fetch new trends if cache is empty or outdated
                    fetcher = TrendFetcher()
                    articles = fetcher.fetch_articles()
                    
                    # If we got new articles, clear old ones and add new ones
                    if articles:
                        trends_collection.delete_many({})  # Clear old trends
                        
                        for art in articles:
                            title = art.get("title")
                            image = art.get("urlToImage")
                            url = art.get("url")
                            description = art.get("description")
                            author = art.get("author")
                            published_at = art.get("publishedAt")
                            source = art.get("source", {}).get("name")
                            
                            if not title:
                                continue
                                
                            trends_collection.insert_one({
                                "title": title,
                                "image_url": image,
                                "url": url,
                                "description": description,
                                "author": author,
                                "published_at": published_at,
                                "source": source,
                                "timestamp": now,
                            })
                            
                # Get trends from DB
                trend_articles = list(trends_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(4))
                
                if trend_articles:
                    logger.info(f"Successfully retrieved {len(trend_articles)} trend articles from MongoDB")
                    return jsonify({"trends": trend_articles})
                    
                logger.warning("No trends found in MongoDB")
            except Exception as e:
                logger.error(f"Error retrieving from MongoDB: {str(e)}")
        
        # If we got here, either there was no MongoDB connection or no trends in the DB
        # In either case, fetch directly
        logger.info("Fetching trends directly from NewsAPI")
        fetcher = TrendFetcher()
        articles = fetcher.fetch_articles()
        
        trend_articles = []
        for art in articles[:4]:  # Limit to 4 articles
            trend_articles.append({
                "title": art.get("title", "No Title"),
                "image_url": art.get("urlToImage", ""),
                "url": art.get("url", ""),
                "description": art.get("description", ""),
                "author": art.get("author", "Unknown"),
                "published_at": art.get("publishedAt", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
            })
            
        logger.info(f"Successfully fetched {len(trend_articles)} trend articles directly")
        return jsonify({"trends": trend_articles})
    
    except Exception as e:
        logger.error(f"Unhandled error in get_trends: {str(e)}")
        # Use the demo articles as a fallback
        fetcher = TrendFetcher()
        articles = fetcher.get_demo_articles()
        
        trend_articles = []
        for art in articles[:4]:  # Limit to 4 articles
            trend_articles.append({
                "title": art.get("title", "No Title"),
                "image_url": art.get("urlToImage", ""),
                "url": art.get("url", ""),
                "description": art.get("description", ""),
                "author": art.get("author", "Unknown"),
                "published_at": art.get("publishedAt", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
            })
            
        logger.info(f"Using {len(trend_articles)} demo articles as fallback")
        return jsonify({"trends": trend_articles})

# For backward compatibility
@api_blueprint.route("/trends", methods=["GET"])
def api_get_trends():
    return get_trends() 