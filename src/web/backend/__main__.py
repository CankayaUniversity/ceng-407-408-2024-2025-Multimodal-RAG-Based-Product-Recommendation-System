from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from api import register_routes  # Import register_routes instead of api_blueprint
from auth.auth import auth_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure static file serving for uploads
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_photos'), exist_ok=True)

# Register the API blueprint with all routes
api_blueprint = register_routes()
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Serve static files from uploads directory
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)