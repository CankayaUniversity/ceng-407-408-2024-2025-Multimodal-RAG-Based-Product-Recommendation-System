from flask import request, jsonify
from pymongo import MongoClient
from . import api_blueprint
from services import DatabaseService
import os

database_service = DatabaseService()

@api_blueprint.route('/login', methods=['POST'])
def login():
    collection = database_service.get_collection(db_name=os.getenv("MONGO_DB_NAME"), collection_name="users")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = collection.find_one({"email": email, "password": password})
    
    if user:
        return jsonify({"message": "Login successful", "email": email}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401