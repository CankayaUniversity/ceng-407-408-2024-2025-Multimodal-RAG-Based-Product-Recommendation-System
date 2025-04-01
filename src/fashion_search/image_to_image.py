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

class ImageToImageSearch:
    def __init__(self, qdrant_url: str, api_key: str):
        
        qdrant_url = os.getenv("qdrant_url")
        api_key = os.getenv("qdrant_api_key")
        if not qdrant_url or not api_key:
            raise ValueError("qdrant_url or api_key not set in environment.")
        
        
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.fclip = FashionCLIP('fashion-clip')
    
    def search(self, image_url: str, collection_name: str, n_results: int = 5) -> Optional[List[Tuple[models.ScoredPoint, str]]]:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        if 'image' not in response.headers.get('Content-Type', ''):
            raise ValueError("URL does not point to a valid image")

        img = Image.open(io.BytesIO(response.content)).convert('RGB').resize((224, 224))
        img_emb = self.fclip.encode_images([img], batch_size=1)[0]
        img_emb_normalized = img_emb / np.linalg.norm(img_emb)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=img_emb_normalized.tolist(),
            limit=n_results,
            with_payload=True,
            search_params=models.SearchParams(hnsw_ef=128)
        )

        sorted_results = sorted(results, key=lambda x: x.score)[:n_results]

        return [(result, collection_name) for result in sorted_results]
    
    

# if __name__ == "__main__":
    
    
#     qdrant_url = os.getenv("qdrant_url")
#     api_key = os.getenv("qdrant_api_key")
    
#     searcher = ImageToImageSearch(qdrant_url, api_key)
#     results = searcher.search(
#         "https://static.zara.net/photos///2023/I/0/1/p/7614/342/630/3/w/448/7614342630_1_1_1.jpg?ts=1687183159644",
#         "clip_DRESSES_JUMPSUITS"
#     )

#     for idx, (result, col_name) in enumerate(results, 1):
#         print(f"\n#{idx} | Similarity: {1 - result.score:.2f}")
#         print(f"Collection: {col_name}")
#         print(f"Product: {result.payload.get('product_name', 'N/A')}")
#         print(f"Price: {result.payload.get('price', 'N/A')}")
#         print(f"Image: {result.payload.get('image_url', '')}")
        