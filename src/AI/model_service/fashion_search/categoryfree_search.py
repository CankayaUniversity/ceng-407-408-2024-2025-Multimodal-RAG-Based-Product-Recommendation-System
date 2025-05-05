import io
import numpy as np
import requests
from typing import List, Optional, Tuple, Union
from PIL import Image
from qdrant_client import QdrantClient, models
from fashion_clip.fashion_clip import FashionCLIP
import os
from dotenv import load_dotenv


load_dotenv()


class CategoryFreeSearch:
    def __init__(self):
        VECTORDB_URL = os.getenv("VECTORDB_URL")
        api_key = os.getenv("VECTORDB_API")
        if not VECTORDB_URL or not api_key:
            raise ValueError("VECTORDB_URL or VECTORDB_API not set in environment.")
        
        self.client = QdrantClient(url=VECTORDB_URL, api_key=api_key)
        self.fclip = FashionCLIP('fashion-clip')
    
    def _get_image_embedding(self, image_input: Union[str, Image.Image]) -> np.ndarray:
        """
        Retrieve and encode an image input to get its normalized embedding.
        Accepts either a URL (str) or a PIL.Image.
        """
        if isinstance(image_input, str):
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(image_input, headers=headers, timeout=10)
            response.raise_for_status()
            if 'image' not in response.headers.get('Content-Type', ''):
                raise ValueError("URL does not point to a valid image")
            img = Image.open(io.BytesIO(response.content)).convert('RGB').resize((224, 224))
        elif isinstance(image_input, Image.Image):
            img = image_input.convert('RGB').resize((224, 224))
        else:
            raise ValueError("Unsupported image input type")
        
        img_emb = self.fclip.encode_images([img], batch_size=1)[0]
        norm = np.linalg.norm(img_emb)
        return img_emb if norm == 0 else img_emb / norm
    
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Encode a text string and return its normalized embedding."""
        text_emb = self.fclip.encode_text([text], batch_size=1)[0]
        norm = np.linalg.norm(text_emb)
        return text_emb if norm == 0 else text_emb / norm

    def search(self, text: Optional[str] = None, image: Optional[Union[str, Image.Image]] = None, n_results: int = 5) -> Optional[List[Tuple[models.ScoredPoint, str]]]:
        """
        Perform a multimodal search across all collections by combining text and image embeddings.
        At least one modality must be provided.
        """
        if not text and not image:
            raise ValueError("Please provide at least a text or image input.")
        
        embeddings = []
        if image:
            print("Processing image input...")
            embeddings.append(self._get_image_embedding(image))
        if text:
            print("Processing text input...")
            embeddings.append(self._get_text_embedding(text))
        
        # Average the embeddings (if more than one modality is provided)
        query_vector = np.mean(embeddings, axis=0).tolist()
        
        try:
            collections = self.client.get_collections()
        except Exception as e:
            print(f"Error retrieving collections: {str(e)}")
            return None
        
        valid_collections = [col.name for col in collections.collections]
        if not valid_collections:
            print("No valid collections found.")
            return None
        
        all_results = []
        for collection_name in valid_collections:
            try:
                results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=n_results,
                    with_payload=True,
                    search_params=models.SearchParams(hnsw_ef=128)
                )
                all_results.extend([(result, collection_name) for result in results])
            except Exception as e:
                print(f"Error searching collection {collection_name}: {str(e)}")
                continue
      
        sorted_results = sorted(all_results, key=lambda x: x[0].score)
        final_results = []
        seen_ids = set()
        for result, col_name in sorted_results:
            unique_id = result.payload.get('product_id') or result.id
            if unique_id not in seen_ids:
                seen_ids.add(unique_id)
                final_results.append((result, col_name))
            if len(final_results) >= n_results:
                break
        
        return final_results


# categoryfree_search = CategoryFreeSearch