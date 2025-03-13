
from qdrant_client.models import PointStruct
import pandas as pd
from vectorization import images_to_vectors
from utils import extract_all_images
from vector_db import client, create_collection, insert_db


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
        
        

df_women = pd.read_csv("zara_women.csv")

df_men = pd.read_csv("datasets/zara_men.csv")

base_collection_women = "zara_women"

base_collection_men = "clip_men"


target_categories_women = [
    "SPECIAL_PRICES", "WAISTCOATS_GILETS", "BASICS", "BLAZERS",
    "DRESSES_JUMPSUITS", "JACKETS", "KNITWEAR", "SHIRTS", "SHOES"
]

target_categories_men = [
    "BLAZERS", "HOODIES_SWEATSHIRTS", "LINEN", "OVERSHIRTS",
    "POLO SHIRTS", "SHIRTS", "SHOES", "SHORTS", "SWEATERS_CARDIGANS",
    "T-SHIRTS", "TROUSERS"
]

# insert women data
for category in target_categories_women:
    df_of_category = df_women[df_women['category'] == category]
    initialize_collection(client, df_of_category,base_collection_name=base_collection_women, category=category)
    

# insert men data
for category in target_categories_men:
    df_of_category = df_men[df_men['category'] == category]
    initialize_collection(client, df_of_category,base_collection_name=base_collection_men, category=category)
    
    
    