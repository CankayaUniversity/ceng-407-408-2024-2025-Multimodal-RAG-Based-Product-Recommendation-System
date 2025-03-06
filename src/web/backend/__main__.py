from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/test", methods=["POST"])
def test():
    body = request.data
    return jsonify({"message": "Successfully executed."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
