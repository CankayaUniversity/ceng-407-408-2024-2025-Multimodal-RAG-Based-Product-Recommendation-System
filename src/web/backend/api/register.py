from flask import Flask, request, jsonify
from pymongo import MongoClient
from . import api_blueprint
from services import DatabaseService
import os


database_service = DatabaseService()

@api_blueprint.route('/register', methods=['POST'])
def register():
    collection = database_service.get_collection(collection_name="users")

    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    if collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists!'}), 400
    new_user = {'username': username,'email':email, 'password': password}
    collection.insert_one(new_user)
    
    return jsonify({'message': 'User registered successfully!'})