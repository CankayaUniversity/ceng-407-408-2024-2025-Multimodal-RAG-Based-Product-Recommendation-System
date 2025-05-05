from flask import jsonify, request
from . import api_blueprint
from auth import auth_required
from services import DatabaseService

database_service = DatabaseService()

@api_blueprint.route("/get_keywords", methods=["POST", "GET"])
@auth_required
def get_keywords():
    collection = database_service.get_collection(collection_name="user_keywords")
    
    # Safely handle missing or invalid JSON
    data = request.get_json(silent=True)
    if not data or "email" not in data:
        return jsonify({"error": "Missing or invalid 'email' in request"}), 400
    
    email = data["email"]
    
    
    user = collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    preferences = user.get("keywords", [])

    return jsonify({"preferences": preferences}), 200



@api_blueprint.route("/save_keywords", methods=["POST"])
@auth_required
def save_keywords():
    collection = database_service.get_collection(collection_name="user_keywords")
    
    data = request.get_json()
    if not data or "email" not in data or "preferences" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    email = data["email"]
    preferences = data["preferences"]

    result = collection.update_one(
        {"email": email},
        {"$set": {"keywords": preferences}},
        upsert=True  # Create document if it doesn't exist
    )

    return jsonify({"message": "Preferences saved successfully"}), 200