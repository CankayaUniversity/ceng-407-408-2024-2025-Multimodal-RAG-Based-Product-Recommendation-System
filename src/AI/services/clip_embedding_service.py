from sentence_transformers import SentenceTransformer
import requests
from typing import List, Tuple, Optional
from PIL import Image
import io
import numpy as np
import logging
from services.base_embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class ClipEmbeddingService(EmbeddingService):

    def __init__(self):
        logger.info("CLIP Embedding Selected")
        self.model = SentenceTransformer('clip-ViT-B-32')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def image_to_vector(self, image_urls) -> Tuple[Optional[np.ndarray], List[str]]:
        vectors = []
        valid_urls = []

        for url in image_urls:
            try:
                response = requests.get(url, headers=self.headers, stream=True)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content)).convert("RGB")
                    image = image.resize((224, 224))  # resize images
                    vector = self.model.encode(image, show_progress_bar=False)
                    vectors.append(vector)
                    valid_urls.append(url)
                else:
                    print(f"Failed to fetch image: {url}")
            except Exception as e:
                print(f"Error processing image {url}: {e}")

        if vectors:
            return np.mean(vectors, axis=0), valid_urls  # average vector for multiple images
        return None, []
