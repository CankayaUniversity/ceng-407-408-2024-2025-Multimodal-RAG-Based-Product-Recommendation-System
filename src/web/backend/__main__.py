from flask import Flask, request, jsonify
from flask_cors import CORS
from api import api_blueprint
from auth.auth import auth_bp
from api.profile import profile_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)