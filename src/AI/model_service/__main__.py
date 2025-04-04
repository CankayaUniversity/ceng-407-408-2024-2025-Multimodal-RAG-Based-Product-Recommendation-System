import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_methods import rag_pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS
from api import api_blueprint

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_blueprint, url_prefix='/ai')

if __name__ == "__main__":
    
    GOOGLE_API_KEY = os.getenv("google_api_key")
    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is missing! Ensure it's set in the .env file.")
    
    app.run(host="0.0.0.0", port=3002)

    ##
    

    # memory = ConversationBufferMemory(memory_key="chat_history", input_key="query_text", return_messages=True)
    

    # query = "I need a yellow dress for a summer night out. It should have floral prints. Please consider the uploaded image as well."
    # category = "clip_DRESSES_JUMPSUITS"  
    
    # f = open("ornek.txt", "r")
    # image_base64 = f.readline()
    # print(image_base64)
    
    
    # recommendation = rag_pipeline(query, category, image_base64, memory)
    # print("Recommendation:\n", recommendation)
    
    
    # sleep(60)
    
    # #   follow-up query with chat history included
    # followup_query = "I liked that suggestion, but can you recommend a piece with more flowers?"
    # followup_recommendation = rag_pipeline(followup_query, category, image_base64, memory)
    # print("Follow-up Recommendation:\n", followup_recommendation)
