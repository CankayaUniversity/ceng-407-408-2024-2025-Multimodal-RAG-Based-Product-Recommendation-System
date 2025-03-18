from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from services import GeneralConfigService
from services.base_embedding_service import EmbeddingService
import os
from dotenv import load_dotenv
from utils import extract_all_images
import pandas
import logging
from rich.progress import track


load_dotenv()
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, embedding_service: EmbeddingService):
        self.config_service = GeneralConfigService
        self._init_client()
        self.embedding_service = embedding_service

    def _init_client(self):
        logger.info("Connecting QDrant Client")
        self._client = QdrantClient(
            url=self.config_service.database_url,
            api_key=os.getenv("VECTORDB_API"),
        )


    def _create_collection(self, collection_name, size: int = 512, distance: Distance = Distance.COSINE):
        # collection creation
        self._client.create_collection(
            collection_name=collection_name, vectors_config=VectorParams(size=512, distance=Distance.COSINE)
        )
    
    def initialize_collection(self):
        source_dataset = self.config_service.source_dataset
        logger.info(f"Reading {source_dataset}")
        df = pandas.read_csv(source_dataset)
        
        base_collection_name = self.config_service.base_collection_name
        categories = self.config_service.target_categories

        if len(categories) == 0:
            categories = list(df["category"].unique())

        for category in categories:
            
            ID = 1

            collection_name = f"{base_collection_name}_{category}"
            self._create_collection(collection_name=f"{base_collection_name}_{category}")

            df_category = df[df["category"] == category]


            # Insert data into Qdrant
            points = []
            for idx, row in track(df_category.iterrows(), total=df_category.shape[0], description=f"Progressing {category}", disable=False):
                
                image_urls = extract_all_images(row["Product_Image"])  # Get all images
                if not image_urls:
                    continue  # Skip products with no images

                vector, valid_urls= self.embedding_service.image_to_vector(image_urls)  # Compute vector representation
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

                self._client.upsert(collection_name=collection_name, points=[PointStruct(
                    id=ID,
                    vector=vector.tolist(),
                    payload= payload,
                )])
                ID +=1
