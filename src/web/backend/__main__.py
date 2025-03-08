from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/test", methods=["POST"])
def test():
    user_message = request.json.get("message", "")
    bot_response = f"Echo: {user_message}"  # Simple echo response
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)