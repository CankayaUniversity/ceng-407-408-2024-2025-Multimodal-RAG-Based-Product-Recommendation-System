import json
from flask import jsonify, request
import requests
from . import api_blueprint
from auth import auth_required
from PIL import Image
import io
from io import BytesIO
import base64
from box import Box

@api_blueprint.route("/chat", methods=["POST"])
@auth_required
def chat():
    body = Box(request.get_json())
    query = body.message
    email = body.email
    category = body.category
    image_base64 = body.imageBase64

    body = {
        "email": email,
        "query": query,
        "image_base64": image_base64,
        "category": category
    }


    response = requests.post(
        "http://localhost:3002/ai/handle_prompt",
        json=body
    )

    response_data = Box(response.json())


    return jsonify({"message": "Successfully executed.","response":response_data.response}), 200