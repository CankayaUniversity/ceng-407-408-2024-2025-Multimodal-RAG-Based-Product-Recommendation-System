from datetime import datetime, timedelta
from pymongo import MongoClient
from utils.Classes.TrendFetcher import TrendFetcher
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_and_cache_trends():
    
    client = MongoClient(
        os.getenv("MONGO_URL"),
        username=os.getenv("MONGO_USERNAME"),
        password=os.getenv("MONGO_PASSWORD"),
    )
    
    db = client.get_database("trends_db")  
    trends_collection = db.get_collection("trends")

    latest = trends_collection.find_one(sort=[("timestamp", -1)])
    now = datetime.utcnow()

    if not latest or (now - latest["timestamp"] > timedelta(hours=24)):
        try:
            fetcher = TrendFetcher()
            articles = fetcher.fetch_articles()

            for art in articles:
                title = art.get("title")
                image = art.get("urlToImage")
                url = art.get("url")

                if not title or not image:
                    continue

                if trends_collection.find_one({"title": title}):
                    continue

                trends_collection.insert_one({
                    "title": title,
                    "image_url": image,
                    "timestamp": now,
                    "url": url,
                })

        except Exception as e:
            print("Trend fetch error:", e)
