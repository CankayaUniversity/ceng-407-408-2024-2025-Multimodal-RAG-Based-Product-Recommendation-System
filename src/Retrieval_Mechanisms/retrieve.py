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

# Qdrant server connection
client = QdrantClient(
    url="https://bd8424ba-78b3-4911-99d7-246c45a6a7e6.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv("VECTORDB_API"),
)

model = SentenceTransformer('clip-ViT-B-32')

collections = client.get_collections()

collection_names = [collection.name for collection in collections.collections]

collection_names

TEXT = "blue dress"

TEXT_VECTOR = model.encode(TEXT)

# for col in collection_names:
    # get similar images from qdrant
search_results = client.search(
    collection_name="zara_women_DRESSES_JUMPSUITS",
    query_vector=TEXT_VECTOR.tolist(),
    limit=5
)

for result in search_results:
    print(f"COLLECTON: {"zara_women_DRESSES_JUMPSUITS"}|ID: {result.id}, Distance: {result.score}, Image URL: {result.payload['image_url']}")

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