from flask import jsonify, request
from . import api_blueprint
from auth import auth_required

@api_blueprint.route("/test", methods=["POST"])
@auth_required
def test():
    body = request.data
    return jsonify({"message": "Successfully executed."}), 200