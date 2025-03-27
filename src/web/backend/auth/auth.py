from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timezone, timedelta
from pathlib import Path

auth_bp = Blueprint('auth', __name__)

path_of_keys = Path.joinpath((Path(__file__).parent.parent), "keys")

def load_keys():
    path_of_private_key = path_of_keys.joinpath("private.pem")
    path_of_public_key = path_of_keys.joinpath("public.pem")
    with open(path_of_private_key, 'r') as f:
        private = f.read()
    with open(path_of_public_key, 'r') as f:
        public = f.read()
    return private, public

PRIVATE_KEY, PUBLIC_KEY = load_keys()

TOKEN_EXP_MINUTES = 5

def create_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXP_MINUTES)
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return token

def verify_token(token):
    try:
        data = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        decoded = verify_token(token)
        if not decoded:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return f(*args, **kwargs)
    return decorated_function