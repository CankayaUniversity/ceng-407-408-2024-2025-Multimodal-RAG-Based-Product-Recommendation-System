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

#
# Body Measurements and Analysis Endpoints
#

@api_blueprint.route('/gemini/body-measurements', methods=['POST'])
def detect_gemini_body_measurements():
    """Detect estimated body measurements from a full-body photo"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Check if image is provided
    if 'image' not in request.files and 'image_data' not in request.form:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        # Process the image data
        image_data = None
        
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            image_bytes = image_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
        elif 'image_data' in request.form:
            # Handle base64-encoded image string
            image_data = request.form['image_data']
            # If it's a data URL, extract just the base64 part
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
        
        if not image_data:
            return jsonify({"error": "Failed to process image data"}), 400
        
        # Call Gemini service to detect body measurements
        measurements = gemini_service.detect_body_measurements(image_data)
        
        # Check if there was an error
        if "error" in measurements:
            return jsonify({
                "error": measurements["error"],
                "message": "Failed to detect body measurements",
                "details": measurements.get("text_response", "No details available")
            }), 500
        
        return jsonify({
            "message": "Body measurements detected successfully",
            "data": measurements
        })
    except Exception as e:
        current_app.logger.error(f"Error detecting body measurements: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/gemini/outfit-analysis', methods=['POST'])
def analyze_outfit():
    """Analyze an outfit image to identify items and provide styling feedback"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Check if image is provided
    if 'image' not in request.files and 'image_data' not in request.form and 'image_url' not in request.form:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        # Process the image data
        image_data = None
        
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            image_bytes = image_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
        elif 'image_data' in request.form:
            # Handle base64-encoded image string
            image_data = request.form['image_data']
            # If it's a data URL, extract just the base64 part
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
        elif 'image_url' in request.form:
            # Handle image URL
            image_data = request.form['image_url']
        
        if not image_data:
            return jsonify({"error": "Failed to process image data"}), 400
        
        # Call Gemini service to analyze the outfit
        analysis = gemini_service.analyze_outfit_image(image_data)
        
        # Check if there was an error
        if "error" in analysis:
            return jsonify({
                "error": analysis["error"],
                "message": "Failed to analyze outfit",
                "details": analysis.get("text_response", "No details available")
            }), 500
        
        return jsonify({
            "message": "Outfit analyzed successfully",
            "data": analysis
        })
    except Exception as e:
        current_app.logger.error(f"Error analyzing outfit: {str(e)}")
        return jsonify({"error": str(e)}), 500

#
# AI Stylist Advice Endpoints
#

@api_blueprint.route('/gemini/stylist-advice', methods=['POST'])
def get_stylist_advice():
    """Get AI stylist advice for specific fashion questions or situations"""
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
    
    is_valid, error_message = validate_required_fields(data, ['query'])
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    try:
        # Extract parameters from request
        query = data['query']
        user_profile = data.get('user_profile')
        
        # Call Gemini service to generate stylist advice
        advice = gemini_service.generate_stylist_advice(query, user_profile)
        
        return jsonify({
            "message": "Stylist advice generated successfully",
            "data": {
                "query": query,
                "advice": advice,
                "generated_at": datetime.now().isoformat()
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error generating stylist advice: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/gemini/seasonal-wardrobe', methods=['POST'])
def plan_seasonal_wardrobe():
    """Generate a seasonal wardrobe plan based on existing items and user preferences"""
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
    
    is_valid, error_message = validate_required_fields(data, ['season', 'existing_items', 'user_preferences'])
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    try:
        # Extract parameters from request
        season = data['season']
        existing_items = data['existing_items']
        user_preferences = data['user_preferences']
        
        # Call Gemini service to generate seasonal wardrobe plan
        wardrobe_plan = gemini_service.plan_seasonal_wardrobe(
            season=season,
            existing_items=existing_items,
            user_preferences=user_preferences
        )
        
        # Check if there was an error
        if "error" in wardrobe_plan:
            return jsonify({
                "error": wardrobe_plan["error"],
                "message": "Failed to generate wardrobe plan",
                "details": wardrobe_plan.get("text_response", "No details available")
            }), 500
        
        return jsonify({
            "message": "Seasonal wardrobe plan generated successfully",
            "data": wardrobe_plan
        })
    except Exception as e:
        current_app.logger.error(f"Error generating wardrobe plan: {str(e)}")
        return jsonify({"error": str(e)}), 500 