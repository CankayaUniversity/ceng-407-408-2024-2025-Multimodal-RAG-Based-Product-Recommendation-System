from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from pymongo import MongoClient
import os

# MongoDB bağlantısı
client = MongoClient(
            os.getenv("MONGO_URL"),
            username=os.getenv("MONGO_USERNAME"),
            password=os.getenv("MONGO_PASSWORD"),
        )

db = client.get_database("sample_mflix")

def get_memory_for_user(email: str):
    chat_history = MongoDBChatMessageHistory(
        connection_string=os.getenv("MONGO_URL_COMBINED"),
        database_name="sample_mflix",
        session_id=email,
        collection_name="chat_histories"
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=chat_history,
        input_key="query_text",
        return_messages=True
    )
    return memory
