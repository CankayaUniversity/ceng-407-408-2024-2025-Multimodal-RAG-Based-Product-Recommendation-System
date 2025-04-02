import json
from flask import jsonify, request
from . import api_blueprint
from auth import auth_required
from PIL import Image
import io
from io import BytesIO
import base64

@api_blueprint.route("/chat", methods=["POST"])
@auth_required
def chat():
    body = json.loads(request.data)
    image = None
    
    if body["imageBase64"]:
        image64 = body["imageBase64"]
        if image64.startswith("data:"):
            image64 = image64.split(",")[1]

        image_data = base64.b64decode(image64)
        image = Image.open(io.BytesIO(image_data))




    return jsonify({"message": "Successfully executed.","response":"sa"}), 200