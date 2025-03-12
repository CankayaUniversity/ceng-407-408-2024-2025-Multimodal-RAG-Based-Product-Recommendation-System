# -*- coding: utf-8 -*-

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import requests
from PIL import Image
import io
import numpy as np
import pandas as pd
import json

load_dotenv()

from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

# Qdrant server connection
client = QdrantClient(
    url="https://bd8424ba-78b3-4911-99d7-246c45a6a7e6.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv("VECTORDB_API"),
)

model = SentenceTransformer('clip-ViT-B-32')
multimodal_ef = OpenCLIPEmbeddingFunction()

collections = client.get_collections()

collection_names = [collection.name for collection in collections.collections]

collection_names

TEXT = "black dress"

TEXT_VECTOR = multimodal_ef._encode_text(TEXT)# model.encode(TEXT)

# for col in collection_names:
    # get similar images from qdrant
search_results = client.search(
    collection_name="clip_test",
    query_vector=TEXT_VECTOR.tolist(),
    limit=20
)

for result in search_results:
    print(f"COLLECTON: {"clip_test"}|ID: {result.id}, Distance: {result.score}, Image URL: {result.payload['image_url']}")

# COLLECTON: zara_women_DRESSES_JUMPSUITS|ID: 351, Distance: 0.28636092, Image URL: https://static.zara.net/photos///2023/I/0/1/p/7812/575/420/2/w/448/7812575420_1_1_1.jpg?ts=1686581672390
# COLLECTON: zara_women_DRESSES_JUMPSUITS|ID: 152, Distance: 0.28332675, Image URL: https://static.zara.net/photos///2023/I/0/1/p/7775/588/404/2/w/448/7775588404_1_1_1.jpg?ts=1685693893697
# COLLECTON: zara_women_DRESSES_JUMPSUITS|ID: 148, Distance: 0.28044307, Image URL: https://static.zara.net/photos///2023/I/0/1/p/2712/845/400/2/w/448/2712845400_1_1_1.jpg?ts=1692258405355
# COLLECTON: zara_women_DRESSES_JUMPSUITS|ID: 84, Distance: 0.2738852, Image URL: https://static.zara.net/photos///2023/I/0/1/p/3067/274/112/2/w/448/3067274112_1_1_1.jpg?ts=1691152511654
# COLLECTON: zara_women_DRESSES_JUMPSUITS|ID: 86, Distance: 0.2690944, Image URL: https://static.zara.net/photos///2023/I/0/1/p/7921/629/080/2/w/448/7921629080_1_1_1.jpg?ts=1685703813341

def query_images(client, query_text, category, collection_name, model, n_results=3):
    """
    Queries Qdrant with a text input and returns the top-matching images using CLIP embeddings.

    Parameters:
    - client: QdrantClient instance
    - query_text: User input text
    - category: Category to filter results
    - collection_name: Name of the Qdrant collection
    - model: CLIP model for text encoding
    - n_results: Number of results to retrieve (default: 3)
    """
    # Encode the query text into a vector using CLIP
    query_vector = model.encode([query_text])[0].tolist()

    # Perform the search in Qdrant
    search_results = client.search(
        collection_name=f"{collection_name}_{category}",
        query_vector=query_vector,
        limit=n_results,
        with_payload=True  # Retrieve metadata with results
    )

    # Process and print results
    print(f"Results for query: {query_text}")
    for result in search_results:
        metadata = result.payload
        print(f"ID: {result.id}, Distance: {result.score}")
        print(f"Product Name: {metadata['product_name']}")
        print(f"Image URL: {metadata['image_url']}")
        print(f"Price: {metadata['price']}")
        print(f"Details: {metadata['details']}")
        print("-" * 50)

    return search_results