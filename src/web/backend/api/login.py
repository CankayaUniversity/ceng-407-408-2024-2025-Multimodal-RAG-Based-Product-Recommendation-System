from flask import request, jsonify
from . import api_blueprint
from services import DatabaseService
from auth import create_token

database_service = DatabaseService()

@api_blueprint.route('/login', methods=['POST'])
def login():
    collection = database_service.get_collection(collection_name="users")
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = collection.find_one({"email": email, "password": password})
    
    if user:
        token = create_token(email=email)
        return jsonify({"message": "Login successful", "email": email, "token":token }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401