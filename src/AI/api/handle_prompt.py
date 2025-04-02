import json
from flask import jsonify, request
from . import api_blueprint
from langchain_methods import rag_pipeline
from langchain.memory import ConversationBufferMemory
from box import Box

# temp global (further changes require user based)
memory = ConversationBufferMemory(memory_key="chat_history", input_key="query_text", return_messages=True)

@api_blueprint.route("/handle_prompt", methods=["POST"])
def handle_prompt():
    data = Box(request.get_json())
    
    recommendation = rag_pipeline(data.query, data.category, data.image_base64, memory)



    return jsonify({"message": "Successfully executed.","response":recommendation}), 200