import json
from flask import jsonify, request, current_app
import requests
from . import api_blueprint
from auth import auth_required
from box import Box
from utils.compress_base64_image import compress_base64_image
import traceback

@api_blueprint.route("/chat", methods=["POST"])
def chat():
    try:
        # Extract the auth token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token locally first to avoid unnecessary calls
        # Import here to avoid circular imports
        from auth.auth import verify_token as auth_verify_token
        user_data = auth_verify_token(token)
        if not user_data:
            current_app.logger.warning("Token verification failed in chat endpoint")
            return jsonify({
                "error": "Authentication failed", 
                "details": "Your session has expired. Please log in again."
            }), 401
        
        # Parse request body
        body = Box(request.get_json())
        query = body.message
        email = body.email
        category = body.category
        
        # Safely get imageBase64 with a default of None if it doesn't exist
        image_base64 = None
        if hasattr(body, 'imageBase64'):
            image_base64 = body.imageBase64
        
        # Only compress image if it exists
        compressed_image_base64 = None
        if image_base64:
            compressed_image_base64 = compress_base64_image(image_base64)

        # Prepare request to model service
        request_body = {
            "email": email,
            "query": query,
            "image_base64": compressed_image_base64,
            "category": category
        }

        current_app.logger.info(f"Sending request to model service for user: {email}, query: {query[:50]}...")
        
        # Make request to model service
        try:
            response = requests.post(
                "http://localhost:3002/ai/cat_free", # for docker host is: model_service:3002
                json=request_body,
                headers={"Authorization": f"Bearer {token}"},
                timeout=1000  # Set a reasonable timeout
            )
            
            # Check for response errors
            if not response.ok:
                current_app.logger.error(f"Model service error: {response.status_code} - {response.text}")
                if response.status_code == 401:
                    return jsonify({"error": "Authentication failed", "details": "Your session has expired. Please log in again."}), 401
                return jsonify({"error": "Model service error", "details": response.text}), response.status_code

            response_data = Box(response.json())
            current_app.logger.info(f"Received response from model service")

            return jsonify({"message": "Successfully executed.", "response": response_data.response}), 200
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error connecting to model service: {str(e)}")
            return jsonify({"error": "Cannot connect to model service", "details": str(e)}), 503
            
    except Exception as e:
        current_app.logger.error(f"Error in chat endpoint: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500