import json
from flask import jsonify, request
import requests
from . import api_blueprint
from auth import auth_required
from box import Box
from utils.compress_base64_image import compress_base64_image

@api_blueprint.route("/chat", methods=["POST"])
@auth_required
def chat():
    body = Box(request.get_json())
    query = body.message
    email = body.email
    category = body.category
    image_base64 = body.imageBase64
    
    compressed_image_base64 = compress_base64_image(image_base64)

    body = {
        "email": email,
        "query": query,
        "image_base64": compressed_image_base64,
        "category": category
    }


    response = requests.post(
        "http://model_service:3002/ai/cat_free", # for docker host is: model_service:3002 (handle_prompt) (cat_free)
        json=body
    )

    response_data = Box(response.json())


    return jsonify({"message": "Successfully executed.","response":response_data.response}), 200