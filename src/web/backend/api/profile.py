from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import time
import base64
from pymongo import MongoClient
from bson import ObjectId
import io
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)  # Only show errors
logger = logging.getLogger(__name__)

profile_bp = Blueprint('profile', __name__)

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URL_COMBINED')
if not MONGO_URI:
    raise ValueError("MongoDB URI not found in environment variables")

client = MongoClient(MONGO_URI)
db = client['user_photos']  # Changed database name
user_photos_collection = db['user_photos_collection']  # Changed collection name

# Configure upload folder
UPLOAD_FOLDER = Path('uploads/profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Read the file and convert to base64
            file_content = file.read()
            base64_image = base64.b64encode(file_content).decode('utf-8')
            
            # Get email from the request
            email = request.headers.get('X-User-Email')
            print(f"Attempting to upload photo for email: {email}")
            
            if not email:
                return jsonify({'error': 'User not authenticated'}), 401
            
            # Update user document with the base64 image
            try:
                result = user_photos_collection.update_one(
                    {'email': email},
                    {'$set': {
                        'profile_photo': base64_image,
                        'profile_photo_updated_at': time.time()
                    }},
                    upsert=True
                )
                print(f"Database update result: {result.modified_count} documents modified")
                
                return jsonify({
                    'message': 'Photo uploaded successfully',
                    'photo_url': f'data:image/{file.content_type};base64,{base64_image}'
                }), 200
                
            except Exception as e:
                print(f"Database error: {str(e)}")
                return jsonify({'error': f'Failed to save photo: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@profile_bp.route('/get-profile-photo', methods=['GET'])
def get_profile_photo():
    try:
        email = request.headers.get('X-User-Email')
        print(f"Getting photo for email: {email}")
        
        if not email:
            return jsonify({'error': 'User not authenticated'}), 401
        
        try:
            user = user_photos_collection.find_one({'email': email})
            if user and 'profile_photo' in user:
                return jsonify({
                    'photo_url': f'data:image/jpeg;base64,{user["profile_photo"]}'
                }), 200

            # Placeholder: 1x1 transparent PNG
            placeholder_base64 = (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
                "ASsJTYQAAAAASUVORK5CYII="
            )
            return jsonify({
                'photo_url': f'data:image/png;base64,{placeholder_base64}'
            }), 200

        except Exception as e:
            print(f"Database error: {str(e)}")
            return jsonify({'error': f'Failed to get photo: {str(e)}'}), 500
    except Exception as e:
        print(f"Get photo error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500 