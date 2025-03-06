from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    bot_response = f"Echo: {user_message}"  # Simple echo response
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
