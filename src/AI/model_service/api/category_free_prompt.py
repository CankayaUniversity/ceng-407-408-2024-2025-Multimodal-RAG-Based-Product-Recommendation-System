from flask import jsonify, request, current_app
from . import api_blueprint
from langchain_methods import get_memory_for_user
from langchain_methods.rag_pipeline_categoryfree import rag_pipeline
from box import Box
import os
import jwt
import logging
import traceback
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to verify token
def verify_token(token):
    try:
        # First try with the JWT_SECRET (HS256)
        jwt_secret = os.getenv('JWT_SECRET')
        if jwt_secret:
            try:
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                logger.info("Token verified using JWT_SECRET (HS256)")
                return payload
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.warning(f"HS256 verification failed: {str(e)}")
                # Fall through to try the next method
        
        # If HS256 fails or JWT_SECRET not available, try to validate through a direct call
        # to the backend auth service
        try:
            response = requests.get(
                "http://localhost:3001/auth/check",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            if response.ok:
                logger.info("Token verified via backend auth service")
                return response.json().get('user', {})
            else:
                logger.warning(f"Backend auth service verification failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to backend auth service: {str(e)}")
            # Fall through to try final method
            
        # As a last resort, try with RS256 and public key directly
        public_key_path = os.environ.get("PUBLIC_KEY_PATH", "../../../web/backend/keys/public.pem")
        try:
            if os.path.exists(public_key_path):
                with open(public_key_path, 'r') as f:
                    public_key = f.read()
                payload = jwt.decode(token, public_key, algorithms=["RS256"])
                logger.info("Token verified using RS256 public key")
                return payload
            else:
                logger.warning(f"Public key not found at {public_key_path}")
        except Exception as e:
            logger.warning(f"RS256 verification failed: {str(e)}")
            
        return None
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {str(e)}")
        return None

@api_blueprint.route("/cat_free", methods=["POST"])
def cat_free():
    try:
        # Check authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            return jsonify({"error": "Authorization required"}), 401
            
        token = auth_header.split(' ')[1]
        # Verify the token
        payload = verify_token(token)
        if not payload:
            logger.warning("Token verification failed")
            return jsonify({"error": "Invalid or expired token"}), 401
            
        # Parse request data
        data = Box(request.get_json())

        if not data.email or not data.query or not data.category:
            logger.warning("Missing required fields in request")
            return jsonify({
                "message": "Bad request.",
                "response": "Missing required fields"
            }), 400

        logger.info(f"Processing request for user: {data.email}, query: {data.query[:50]}...")
        
        # Get user memory and generate response
        memory = get_memory_for_user(data.email)
        recommendation = rag_pipeline(data.query, data.category, data.image_base64, memory)
        
        logger.info(f"Successfully generated recommendation for {data.email}")

        return jsonify({
            "message": "Successfully executed.",
            "response": recommendation
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing category free prompt: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error", 
            "details": str(e)
        }), 500
