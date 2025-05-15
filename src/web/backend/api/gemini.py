from flask import request, jsonify, current_app
from . import api_blueprint
import jwt
import os
import json
import base64
from datetime import datetime
import sys
import logging

# Add the AI directory to the Python path so we can import the GeminiService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../AI')))
from gemini_service import GeminiService

# Initialize Gemini Service
gemini_service = GeminiService()

# Helper function to verify token
def verify_token(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Helper function to validate required fields
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, None

#
# Outfit Composition Endpoints
#

@api_blueprint.route('/gemini/outfit-composition', methods=['POST'])
def generate_outfit_composition():
    """Generate a complete outfit based on user preferences and optional seed item or theme"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Extract parameters from request
        user_preferences = data.get('user_preferences', {})
        seed_item = data.get('seed_item')
        theme = data.get('theme')
        occasion = data.get('occasion')
        season = data.get('season')
        color_scheme = data.get('color_scheme')
        wardrobe_items = data.get('wardrobe_items')
        
        # We need at least user preferences and either a seed item or theme
        if not user_preferences:
            return jsonify({"error": "User preferences are required"}), 400
        
        if not seed_item and not theme:
            return jsonify({"error": "Either a seed item or theme is required"}), 400
        
        # Call Gemini service to generate the outfit
        outfit = gemini_service.generate_outfit(
            user_preferences=user_preferences,
            seed_item=seed_item,
            theme=theme,
            occasion=occasion,
            season=season,
            color_scheme=color_scheme,
            wardrobe_items=wardrobe_items
        )
        
        # Check if there was an error
        if "error" in outfit:
            return jsonify({
                "error": outfit["error"],
                "message": "Failed to generate outfit",
                "details": outfit.get("text_response", "No details available")
            }), 500
        
        return jsonify({
            "message": "Outfit generated successfully",
            "data": outfit
        })
    except Exception as e:
        current_app.logger.error(f"Error generating outfit: {str(e)}")
        return jsonify({"error": str(e)}), 500 