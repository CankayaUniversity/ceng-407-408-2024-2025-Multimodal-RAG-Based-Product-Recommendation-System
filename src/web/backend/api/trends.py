from flask import jsonify
from . import api_blueprint
from auth import auth_required
from utils.fetch_trends_from_db import fetch_and_cache_trends
from pymongo import MongoClient
import os

@api_blueprint.route("/trends", methods=["GET"])
def trends():
    try:
        
        fetch_and_cache_trends()

        client = MongoClient(
            os.getenv("MONGO_URL"),
            username=os.getenv("MONGO_USERNAME"),
            password=os.getenv("MONGO_PASSWORD"),
        )
        db = client.get_database("trends_db")
        trends_collection = db.get_collection("trends")

        
        latest_trends = trends_collection.find().sort("timestamp", -1).limit(12)

        return jsonify({
            "message": "Trends fetched successfully.",
            "trends": [
                {
                    "id": str(trend["_id"]),
                    "title": trend["title"],
                    "image": trend["image_url"],
                    "url": trend["url"]
                }
                for trend in latest_trends
            ]
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Trend fetch failed.",
            "error": str(e)
        }), 500
