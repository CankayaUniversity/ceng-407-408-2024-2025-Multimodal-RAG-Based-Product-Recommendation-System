import io
import numpy as np
import requests
from typing import List, Optional, Tuple
from PIL import Image
from qdrant_client import QdrantClient, models
from fashion_clip.fashion_clip import FashionCLIP
import os
from dotenv import load_dotenv


load_dotenv()

class TextToImageSearch:
    def __init__(self, collection_name: str):
        
        qdrant_url = os.getenv("qdrant_url")
        api_key = os.getenv("qdrant_api_key")
        if not qdrant_url or not api_key:
            raise ValueError("qdrant_url or api_key not set in environment.")
        
        
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.fclip = FashionCLIP('fashion-clip')
        self.collection_name = collection_name

    def search(self, query_text: str, n_results: int = 5):
        """Perform text-to-image similarity search."""
        text_emb = self.fclip.encode_text([query_text], batch_size=1).ravel()

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=text_emb.tolist(),
            limit=n_results,
            with_payload=True
        )

        return results



# if __name__ == "__main__":

#     searcher = TextToImageSearch(collection_name="clip_DRESSES_JUMPSUITS")
#     results = searcher.search("linen wide leg pants", n_results=5)

#     for idx, result in enumerate(results, 1):
#         print(f"\n#{idx} | Score: {result.score:.2f}")
#         print(f"Product: {result.payload.get('product_name', 'N/A')}")
#         print(f"Price: {result.payload.get('price', 'N/A')}")
#         print(f"Image URL: {result.payload.get('image_url', '')}")