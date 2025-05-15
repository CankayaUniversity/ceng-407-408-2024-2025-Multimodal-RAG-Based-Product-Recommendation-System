from flask import request, jsonify, current_app, Blueprint
from . import api_blueprint
import jwt
import os
import base64
from models.user_photo import UserPhoto
from models.style_profile import StyleProfile

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

# This file is kept as a placeholder for future profile-related endpoints 
