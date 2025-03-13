
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv


load_dotenv()

# Qdrant server connection
client = QdrantClient(
    url="https://bd8424ba-78b3-4911-99d7-246c45a6a7e6.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv("VECTORDB_API"),
)

def create_collection(client, collection_name):
    # collection creation
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )


def insert_db(client, collection_name, points):
    if points:
        client.upsert(collection_name=collection_name, points=points)
        print(f"Inserted {len(points)} products into {collection_name}")
    else:
        print("No valid products with images to insert.")

