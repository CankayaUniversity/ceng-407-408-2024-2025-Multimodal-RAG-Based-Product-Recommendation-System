import json
from flask import jsonify, request
from . import api_blueprint
from auth import auth_required

@api_blueprint.route("/test", methods=["POST"])
@auth_required
def test():
    body = json.loads(request.data)
    echo = "Echo: "
    text = echo + body["message"]
    print(text)
    return jsonify({"message": "Successfully executed.","response":text}), 200