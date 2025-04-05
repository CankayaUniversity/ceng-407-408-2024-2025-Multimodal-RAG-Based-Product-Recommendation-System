from flask import jsonify, request
from . import api_blueprint
from langchain_methods import rag_pipeline, get_memory_for_user
from box import Box

@api_blueprint.route("/handle_prompt", methods=["POST"])
def handle_prompt():
    data = Box(request.get_json())

    if not data.email or not data.query or data.category or data.image_base64:
        return jsonify({
        "message": "Successfully executed.",
        "response": recommendation
    }), 400

    memory = get_memory_for_user(data.email)

    recommendation = rag_pipeline(data.query, data.category, data.image_base64, memory)

    return jsonify({
        "message": "Successfully executed.",
        "response": recommendation
    }), 200
