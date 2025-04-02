import numpy as np
import os
from typing import List, Optional, Tuple
from PIL import Image
from qdrant_client import QdrantClient, models
from fashion_clip.fashion_clip import FashionCLIP
from dotenv import load_dotenv

load_dotenv()

class MultimodalSearch:
    def __init__(self):
        """Initialize Qdrant client and FashionCLIP model."""
        VECTORDB_URL = os.getenv("VECTORDB_URL")
        api_key = os.getenv("VECTORDB_API")
        
        if not VECTORDB_URL or not api_key:
            raise ValueError("VECTORDB_URL or api_key not set in environment.")
        
        self.client = QdrantClient(url=VECTORDB_URL, api_key=api_key)
        self.fclip = FashionCLIP('fashion-clip')

    def get_multimodal_embedding(self, query_text: str, image: Image) -> np.ndarray:
        """Generate a combined multimodal embedding from text and image."""
        text_embedding = self.fclip.encode_text([query_text], batch_size=1).ravel()
        image_embedding = self.fclip.encode_images([image], batch_size=1)[0]

        # Normalize embeddings
        text_embedding /= np.linalg.norm(text_embedding)
        image_embedding /= np.linalg.norm(image_embedding)

        # Combine embeddings (weighted sum)
        combined_embedding = (0.5 * text_embedding) + (0.5 * image_embedding)
        return combined_embedding / np.linalg.norm(combined_embedding)

    def multimodal_search(
        self, query_text: str, image: Image, collection_name: str, n_results: int = 5
    ) -> Optional[List[Tuple[models.ScoredPoint, str]]]:
        """Perform a multimodal search using both text and image embeddings."""
        combined_embedding = self.get_multimodal_embedding(query_text, image)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=combined_embedding.tolist(),
            limit=n_results,
            with_payload=True,
            search_params=models.SearchParams(hnsw_ef=128),
        )

        sorted_results = sorted(results, key=lambda x: x.score)[:n_results]

        return [(result, collection_name) for result in sorted_results]
