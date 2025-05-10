from flask import request, jsonify, current_app, Blueprint
from . import api_blueprint
import jwt
import os
from models.user_profile import StyleProfile, BodyMeasurements, WardrobeItem, UserInteraction, UserPhoto
from datetime import datetime
import uuid
import tempfile
import base64

# Create a dedicated profile blueprint
profile_bp = Blueprint('profile', __name__)

# Helper function to verify token
def verify_token(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Style Profile Endpoints
@profile_bp.route('/profile/style', methods=['GET'])
def get_style_profile():
    """Get the user's style profile"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    profile = StyleProfile.get_by_user_id(user_id)
    if not profile:
        return jsonify({"error": "Style profile not found"}), 404
    
    return jsonify({
        "message": "Style profile retrieved successfully",
        "data": profile.to_dict()
    })

@api_blueprint.route('/profile/style', methods=['GET'])
def api_get_style_profile():
    return get_style_profile()

@profile_bp.route('/profile/style', methods=['POST', 'PUT'])
def create_update_style_profile():
    """Create or update user's style profile"""
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
    
    # Check if profile exists
    existing_profile = StyleProfile.get_by_user_id(user_id)
    
    if existing_profile:
        # Update existing profile
        for key, value in data.items():
            if hasattr(existing_profile, key):
                setattr(existing_profile, key, value)
        
        existing_profile.save()
        return jsonify({
            "message": "Style profile updated successfully",
            "data": existing_profile.to_dict()
        })
    else:
        # Create new profile
        profile = StyleProfile(
            user_id=user_id,
            preferred_colors=data.get('preferred_colors', []),
            preferred_styles=data.get('preferred_styles', []),
            preferred_categories=data.get('preferred_categories', []),
            disliked_colors=data.get('disliked_colors', []),
            disliked_styles=data.get('disliked_styles', []),
            occasion_preferences=data.get('occasion_preferences', {}),
            season_preferences=data.get('season_preferences', {}),
            budget_range=data.get('budget_range', {})
        )
        
        profile.save()
        return jsonify({
            "message": "Style profile created successfully",
            "data": profile.to_dict()
        })

@api_blueprint.route('/profile/style', methods=['POST', 'PUT'])
def api_create_update_style_profile():
    return create_update_style_profile()

# Body Measurements Endpoints
@profile_bp.route('/profile/measurements', methods=['GET'])
def get_body_measurements():
    """Get the user's body measurements"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    measurements = BodyMeasurements.get_by_user_id(user_id)
    if not measurements:
        return jsonify({"error": "Body measurements not found"}), 404
    
    return jsonify({
        "message": "Body measurements retrieved successfully",
        "data": measurements.to_dict()
    })

@api_blueprint.route('/profile/measurements', methods=['GET'])
def api_get_body_measurements():
    return get_body_measurements()

@profile_bp.route('/profile/measurements', methods=['POST', 'PUT'])
def create_update_body_measurements():
    """Create or update user's body measurements"""
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
    
    # Get existing measurements or create new one
    measurements = BodyMeasurements.get_by_user_id(user_id)
    if not measurements:
        measurements = BodyMeasurements(user_id=user_id)
    
    # Update fields from request
    if 'height' in data:
        measurements.height = data['height']
    if 'weight' in data:
        measurements.weight = data['weight']
    if 'chest' in data:
        measurements.chest = data['chest']
    if 'waist' in data:
        measurements.waist = data['waist']
    if 'hips' in data:
        measurements.hips = data['hips']
    if 'inseam' in data:
        measurements.inseam = data['inseam']
    if 'shoulders' in data:
        measurements.shoulders = data['shoulders']
    if 'sleeve_length' in data:
        measurements.sleeve_length = data['sleeve_length']
    if 'neck' in data:
        measurements.neck = data['neck']
    if 'body_shape' in data:
        measurements.body_shape = data['body_shape']
    if 'fit_preference' in data:
        measurements.fit_preference = data['fit_preference']
    
    measurements.save()
    
    return jsonify({
        "message": "Body measurements updated successfully",
        "data": measurements.to_dict()
    })

@api_blueprint.route('/profile/measurements', methods=['POST', 'PUT'])
def api_create_update_body_measurements():
    return create_update_body_measurements()

# Body Measurements Detection Endpoint
@profile_bp.route('/profile/measurements/detect', methods=['POST'])
def detect_body_measurements():
    """Use computer vision to estimate body measurements from a photo"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Check if image is sent
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    
    try:
        # TODO: Replace with actual Gemini Vision API call to analyze the image
        # For now, we'll return mock data
        
        # Get existing measurements or create new one
        measurements = BodyMeasurements.get_by_user_id(user_id)
        if not measurements:
            measurements = BodyMeasurements(user_id=user_id)
        
        # Mock estimated measurements
        estimated_measurements = {
            "height": 175,  # in cm
            "body_shape": "rectangle",
            "fit_preference": "regular"
        }
        
        # Update with estimated values
        measurements.height = estimated_measurements["height"]
        measurements.body_shape = estimated_measurements["body_shape"]
        measurements.fit_preference = estimated_measurements["fit_preference"]
        
        measurements.save()
        
        return jsonify({
            "message": "Body measurements estimated successfully",
            "data": {
                "estimated": estimated_measurements,
                "full_profile": measurements.to_dict()
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in body measurement detection: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User Wardrobe Endpoints
@profile_bp.route('/profile/wardrobe', methods=['GET'])
def get_wardrobe():
    """Get the user's wardrobe items"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    items = WardrobeItem.get_user_wardrobe(user_id)
    
    return jsonify({
        "message": "Wardrobe items retrieved successfully",
        "data": [item.to_dict() for item in items]
    })

@api_blueprint.route('/profile/wardrobe', methods=['GET'])
def api_get_wardrobe():
    return get_wardrobe()

@profile_bp.route('/profile/wardrobe', methods=['POST'])
def add_wardrobe_item():
    """Add an item to user's wardrobe"""
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
    
    required_fields = ['category']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new wardrobe item
    item = WardrobeItem(
        user_id=user_id,
        product_id=data.get('product_id'),
        category=data.get('category'),
        color=data.get('color'),
        style=data.get('style'),
        season=data.get('season'),
        occasions=data.get('occasions'),
        image_url=data.get('image_url'),
        product_name=data.get('product_name'),
        custom_name=data.get('custom_name'),
        purchased_date=data.get('purchased_date')
    )
    
    item.save()
    
    return jsonify({
        "message": "Wardrobe item added successfully",
        "data": item.to_dict()
    })

@api_blueprint.route('/profile/wardrobe', methods=['POST'])
def api_add_wardrobe_item():
    return add_wardrobe_item()

@profile_bp.route('/profile/wardrobe/<item_id>', methods=['DELETE'])
def delete_wardrobe_item(item_id):
    """Delete an item from user's wardrobe"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Get the item and check ownership
    item = WardrobeItem.get_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    if item.user_id != user_id:
        return jsonify({"error": "Unauthorized to delete this item"}), 403
    
    # Delete the item
    # Implement deletion logic here
    
    return jsonify({
        "message": "Wardrobe item deleted successfully"
    })

# Seasonal Wardrobe Planning
@profile_bp.route('/profile/wardrobe/seasonal-plan', methods=['GET'])
def get_seasonal_plan():
    """Get seasonal wardrobe plan recommendations"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Get user's style profile and wardrobe
    profile = StyleProfile.get_by_user_id(user_id)
    wardrobe = WardrobeItem.get_user_wardrobe(user_id)
    
    if not profile:
        return jsonify({"error": "Style profile not found. Please create a style profile first."}), 404
    
    # Get the season from query parameter (default to current season)
    season = request.args.get('season', 'spring')  # spring, summer, fall, winter
    
    # TODO: Use Gemini API to generate seasonal wardrobe plan based on profile and wardrobe
    # For now, return mock data
    
    # Simplified logic to determine what items user needs for the season
    current_items = [item for item in wardrobe if season in item.season]
    
    seasonal_plan = {
        "season": season,
        "existing_items": [item.to_dict() for item in current_items],
        "recommended_additions": [
            {
                "category": "Jacket",
                "reason": "You don't have a lightweight jacket for cool evenings",
                "style": "Casual",
                "color": "Navy"
            },
            {
                "category": "Dress",
                "reason": "Would complement your existing wardrobe for special occasions",
                "style": "Elegant",
                "color": "Burgundy"
            }
        ],
        "outfit_ideas": [
            {
                "occasion": "Casual Day Out",
                "items": [item.id for item in current_items[:3]],
                "missing_items": ["Lightweight scarf"]
            },
            {
                "occasion": "Work",
                "items": [item.id for item in current_items[1:4]],
                "missing_items": ["Blazer"]
            }
        ]
    }
    
    return jsonify({
        "message": f"Seasonal wardrobe plan for {season} generated successfully",
        "data": seasonal_plan
    })

# User Interaction Tracking
@profile_bp.route('/profile/interactions', methods=['POST'])
def track_interaction():
    """Track user interaction with a product"""
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
    
    required_fields = ['product_id', 'interaction_type']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new interaction
    interaction = UserInteraction(
        user_id=user_id,
        product_id=data['product_id'],
        interaction_type=data['interaction_type'],
        category=data.get('category'),
        product_data=data.get('product_data')
    )
    
    interaction.save()
    
    return jsonify({
        "message": "User interaction tracked successfully"
    })

@api_blueprint.route('/profile/interactions', methods=['POST'])
def api_track_interaction():
    return track_interaction()

@profile_bp.route('/profile/interactions', methods=['GET'])
def get_interactions():
    """Get user's product interactions"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    
    # Get interaction type from query parameter (optional)
    interaction_type = request.args.get('type')
    
    interactions = UserInteraction.get_user_interactions(
        user_id, 
        limit=int(request.args.get('limit', 100)),
        interaction_type=interaction_type
    )
    
    return jsonify({
        "message": "User interactions retrieved successfully",
        "data": [interaction.to_dict() for interaction in interactions]
    })

@api_blueprint.route('/profile/interactions', methods=['GET'])
def api_get_interactions():
    return get_interactions()

# Profile Photo Endpoints
@profile_bp.route('/upload-photo', methods=['POST'])
def upload_profile_photo():
    """Upload a profile photo for the user"""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return jsonify({"error": "User email required"}), 400

    if 'photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({"error": "No photo selected"}), 400

    try:
        # Read the photo data and encode as base64
        photo_data = photo.read()
        content_type = photo.content_type
        
        # Convert to base64
        photo_base64 = base64.b64encode(photo_data).decode('utf-8')
        
        # Create or update user photo in database
        user_photo = UserPhoto.get_by_user_id(user_email)
        if user_photo:
            user_photo.photo_data = photo_base64
            user_photo.content_type = content_type
        else:
            user_photo = UserPhoto(
                user_id=user_email,
                photo_data=photo_base64,
                content_type=content_type
            )
        
        user_photo.save()

        return jsonify({
            "message": "Profile photo uploaded successfully",
            "photo_url": f"/api/get-profile-photo?email={user_email}"
        })

    except Exception as e:
        current_app.logger.error(f"Error uploading profile photo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/get-profile-photo', methods=['GET'])
def get_profile_photo():
    """Get the user's profile photo"""
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "User email required"}), 400

    try:
        user_photo = UserPhoto.get_by_user_id(user_email)
        if not user_photo:
            return jsonify({
                "photo_url": "https://via.placeholder.com/150"  # Default photo
            })

        # Return the photo data and content type
        return jsonify({
            "photo_data": user_photo.photo_data,
            "content_type": user_photo.content_type
        })

    except Exception as e:
        current_app.logger.error(f"Error getting profile photo: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Register the endpoints with the main blueprint
@api_blueprint.route('/upload-photo', methods=['POST'])
def api_upload_profile_photo():
    return upload_profile_photo()

@api_blueprint.route('/get-profile-photo', methods=['GET'])
def api_get_profile_photo():
    return get_profile_photo() 
