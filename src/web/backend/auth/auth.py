from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging
import traceback
import os

auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

path_of_keys = Path.joinpath((Path(__file__).parent.parent), "keys")

def load_keys():
    try:
        # Check if keys exist - create them if not
        Path(path_of_keys).mkdir(exist_ok=True)
        
        path_of_private_key = path_of_keys.joinpath("private.pem")
        path_of_public_key = path_of_keys.joinpath("public.pem")
        
        # If keys don't exist, we'll create default ones
        if not path_of_private_key.exists() or not path_of_public_key.exists():
            logger.warning("Keys not found - creating default keys")
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            # Generate a new private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Serialize and save private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key = private_key.public_key()
            
            # Serialize and save public key
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(path_of_private_key, 'wb') as f:
                f.write(private_pem)
                
            with open(path_of_public_key, 'wb') as f:
                f.write(public_pem)
                
            private = private_pem.decode('utf-8')
            public = public_pem.decode('utf-8')
        else:
            # Read existing keys
            with open(path_of_private_key, 'r') as f:
                private = f.read()
            with open(path_of_public_key, 'r') as f:
                public = f.read()
                
        return private, public
    except Exception as e:
        logger.error(f"Error loading keys: {str(e)}\n{traceback.format_exc()}")
        raise RuntimeError(f"Failed to load authentication keys: {str(e)}")

try:
    PRIVATE_KEY, PUBLIC_KEY = load_keys()
except Exception as e:
    logger.error(f"Failed to load keys: {str(e)}")
    # Fallback to JWT_SECRET if keys fail to load
    PRIVATE_KEY = None
    PUBLIC_KEY = None

TOKEN_EXP_MINUTES = 60  # Increasing token lifetime to reduce expiration issues

def create_token(email):
    try:
        # Use RS256 if keys are available, fallback to HS256
        if PRIVATE_KEY and PUBLIC_KEY:
            payload = {
                'email': email,
                'exp': datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXP_MINUTES),
                'iat': datetime.now(timezone.utc)
            }
            token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
            logger.info(f"Created RS256 token for {email} with expiration {TOKEN_EXP_MINUTES} minutes")
        else:
            # Fallback to HS256 with JWT_SECRET
            jwt_secret = os.getenv('JWT_SECRET')
            if not jwt_secret:
                jwt_secret = 'default-secret-key-for-development-only'
                logger.warning("Using default JWT secret - not secure for production!")
                
            payload = {
                'email': email,
                'exp': datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXP_MINUTES),
                'iat': datetime.now(timezone.utc)
            }
            token = jwt.encode(payload, jwt_secret, algorithm="HS256")
            logger.info(f"Created HS256 token for {email} with expiration {TOKEN_EXP_MINUTES} minutes")
            
        return token
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}\n{traceback.format_exc()}")
        raise

def verify_token(token):
    try:
        # First try with RS256
        if PUBLIC_KEY:
            try:
                data = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
                logger.debug(f"Token verified with RS256: {data.get('email')}")
                return data
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.warning(f"RS256 token verification failed: {str(e)}")
                # Fall through to try HS256
        
        # Then try with HS256
        jwt_secret = os.getenv('JWT_SECRET')
        if jwt_secret:
            try:
                data = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                logger.debug(f"Token verified with HS256: {data.get('email')}")
                return data
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.warning(f"HS256 token verification failed: {str(e)}")
        else:
            # Try with default secret as last resort
            try:
                data = jwt.decode(token, 'default-secret-key-for-development-only', algorithms=["HS256"])
                logger.debug(f"Token verified with default secret: {data.get('email')}")
                return data
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.warning(f"Default secret token verification failed: {str(e)}")
                
        return None
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {str(e)}\n{traceback.format_exc()}")
        return None


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Missing or invalid Authorization header")
                return jsonify({'error': 'Authorization header missing or invalid'}), 401

            token = auth_header.split(' ')[1]
            decoded = verify_token(token)
            if not decoded:
                logger.warning("Invalid or expired token")
                return jsonify({
                    'error': 'Invalid or expired token',
                    'details': 'Please log in again to continue.'
                }), 401

            # Store user info in Flask's g object and request for easy access
            g.user = decoded
            request.user = decoded
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in auth_required: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                'error': 'Authentication error', 
                'details': str(e)
            }), 500
    return decorated_function

@auth_bp.route('/check', methods=['GET'])
@auth_required
def check_auth():
    # Return user info from the token
    user_info = g.user
    return jsonify({
        'message': 'Token is valid',
        'user': user_info
    }), 200