from flask import jsonify, request
from . import api_blueprint

@api_blueprint.route("/test", methods=["POST"])
def test():
    body = request.data
    return jsonify({"message": "Successfully executed."}), 200