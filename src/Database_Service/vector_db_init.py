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

def create_collection(client, collection_name):
    # collection creation
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )

# create_collection(client=client, collection_name="zara_man")
# create_collection(client=client, collection_name="zara_women")

ID = 1

# load CLIP model
model = SentenceTransformer('clip-ViT-B-32')

# # URL'den Görseli Yükleyip Vektöre Çevir
# def image_url_to_vector(image_url):
#     try:
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             image = Image.open(io.BytesIO(response.content)).convert("RGB")
#             vector = model.encode(image)
#             return vector
#         else:
#             print(f"failed to fetch image: {image_url}")
#             return None
#     except Exception as e:
#         print(f"error processing")
#         return None


# # Örnek URL
# image_url = "https://static.zara.net/photos///2023/I/1/1/p/6128/110/800/32/w/448/6128110800_1_1_1.jpg?ts=1687266880181"

# # Görseli Vektöre Çevir
# vector = image_url_to_vector(image_url)

df_women = pd.read_csv("zara_women.csv")

# Function to extract all image URLs from the image data column
def extract_all_images(image_data):
    try:
        # Convert string to a list of dictionaries
        image_list = json.loads(image_data.replace("'", "\""))  # Fix single-quote issue for JSON parsing
        if isinstance(image_list, list) and len(image_list) > 0:
            return [list(item.keys())[0] for item in image_list]  # Extract all image URLs
    except Exception as e:
        print(f"Error parsing image data: {e}")
    return None

# Function to get image vectors for all images
def images_to_vectors(image_urls):
    vectors = []
    valid_urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for url in image_urls:
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                image = image.resize((224, 224)) #resize images
                vector = model.encode(image)
                vectors.append(vector)
                valid_urls.append(url)
                print("success")
            else:
                print(f"Failed to fetch image: {url}")
        except Exception as e:
            print(f"Error processing image {url}: {e}")

    if vectors:
        return np.mean(vectors, axis=0), valid_urls  # Average vector for multiple images
    return None

df_women

def insert_db(client, collection_name, points):
    if points:
        client.upsert(collection_name=collection_name, points=points)
        print(f"Inserted {len(points)} products into {collection_name}")
    else:
        print("No valid products with images to insert.")

base_collection = "zara_women"

# # Insert data into Qdrant
# points = []
# for idx, row in df_women.iterrows():
#    # if ID == 200:
#     image_urls= extract_all_images(row["Product_Image"])  # Get all images
#     if not image_urls:
#         continue  # Skip products with no images

#     vector, valid_urls= images_to_vectors(image_urls)  # Compute vector representation
#     if vector is None:
#         continue  # Skip if no valid vector

#     payload = {
#         "image_url":valid_urls[0],
#         "product_name": row["Product_Name"],
#         "link": row["Link"],
#         "price": row["Price"],
#         "details": row["Details"],
#         "category": row["category"],
#         "image_urls": image_urls  # Store all image URLs
#     }

#     #points.append(PointStruct(id=idx, vector=vector.tolist(), payload=payload))
#     client.upsert(collection_name=collection_name, points=[PointStruct(
#         id=ID,
#         vector=vector.tolist(),
#         payload= payload
#     )])
#     ID +=1
#     print(f"Data inserted successfully! | {ID}/{len(df_women)}")

def initialize_collection(client, df,base_collection_name, category):

    ID = 1

    collection_name = f"{base_collection_name}_{category}"
    create_collection(client=client, collection_name=f"{base_collection_name}_{category}")


    # Insert data into Qdrant
    points = []
    for idx, row in df.iterrows():
    # if ID == 200:
        image_urls= extract_all_images(row["Product_Image"])  # Get all images
        if not image_urls:
            continue  # Skip products with no images

        vector, valid_urls= images_to_vectors(image_urls)  # Compute vector representation
        if vector is None:
            continue  # Skip if no valid vector

        payload = {
            "image_url":valid_urls[0],
            "product_name": row["Product_Name"],
            "link": row["Link"],
            "price": row["Price"],
            "details": row["Details"],
            "category": row["category"],
            "image_urls": image_urls  # Store all image URLs
        }

        #points.append(PointStruct(id=idx, vector=vector.tolist(), payload=payload))
        client.upsert(collection_name=collection_name, points=[PointStruct(
            id=ID,
            vector=vector.tolist(),
            payload= payload
        )])
        ID +=1
        print(f"Data inserted successfully! | {ID}/{len(df)}")



target_categories = [
    "SPECIAL_PRICES", "WAISTCOATS_GILETS", "BASICS", "BLAZERS",
    "DRESSES_JUMPSUITS", "JACKETS", "KNITWEAR", "SHIRTS", "SHOES"
]

for category in target_categories:
    df_of_category = df_women[df_women['category'] == category]
    initialize_collection(client, df_of_category,base_collection_name=base_collection, category=category)