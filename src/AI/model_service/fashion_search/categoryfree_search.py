import io
import numpy as np
import requests
from typing import List, Optional, Tuple, Union
from PIL import Image
from qdrant_client import QdrantClient, models
from fashion_clip.fashion_clip import FashionCLIP
import os
from dotenv import load_dotenv
import random
import re


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
        text_emb = self.fclip.encode_text([text], batch_size=1)[0]
        norm = np.linalg.norm(text_emb)
        return text_emb if norm == 0 else text_emb / norm
    
    def _boost_embedding_for_category(self, base_embedding, category_name, boost_factor=0.3):
        """Adjust the embedding vector to better target a specific category"""
        # Create a category-specific embedding
        category_clean = category_name.replace('clip_', '').replace('men_', '')
        category_text = f"a {category_clean.lower().replace('_', ' ')}"
        category_emb = self._get_text_embedding(category_text)
        
        # Blend the embeddings
        boosted_emb = (1-boost_factor) * np.array(base_embedding) + boost_factor * category_emb
        norm = np.linalg.norm(boosted_emb)
        return boosted_emb.tolist() if norm == 0 else (boosted_emb / norm).tolist()
    
    def _boost_embedding_for_color(self, base_embedding, color_name, boost_factor=0.4):
        color_text = f"a {color_name.lower()} color item"
        color_emb = self._get_text_embedding(color_text)
        
        boosted_emb = (1-boost_factor) * np.array(base_embedding) + boost_factor * color_emb
        norm = np.linalg.norm(boosted_emb)
        return boosted_emb.tolist() if norm == 0 else (boosted_emb / norm).tolist()

    def _boost_embedding_for_outfit(self, base_embedding, outfit_type, boost_factor=0.4):
        outfit_text = f"a complete {outfit_type.lower()} outfit"
        outfit_emb = self._get_text_embedding(outfit_text)
        
        boosted_emb = (1-boost_factor) * np.array(base_embedding) + boost_factor * outfit_emb
        norm = np.linalg.norm(boosted_emb)
        return boosted_emb.tolist() if norm == 0 else (boosted_emb / norm).tolist()

    def search(self, text: Optional[str] = None, image: Optional[Union[str, Image.Image]] = None, n_results: int = 5) -> Optional[List[Tuple[models.ScoredPoint, str]]]:
        """
        Perform a multimodal search across all collections by combining text and image embeddings.
        At least one modality must be provided.
        """
        if not text and not image:
            raise ValueError("Please provide at least a text or image input.")
        
        # Print debug information for monitoring
        print(f"CategoryFreeSearch: Received query text: '{text}'")
        
        embeddings = []
        if image:
            print("Processing image input...")
            embeddings.append(self._get_image_embedding(image))
        if text:
            print("Processing text input...")
            embeddings.append(self._get_text_embedding(text))
        
        # Average the embeddings (if more than one modality is provided)
        base_query_vector = np.mean(embeddings, axis=0).tolist()
        
        try:
            collections = self.client.get_collections()
            print(f"Available collections: {[col.name for col in collections.collections]}")
        except Exception as e:
            print(f"Error retrieving collections: {str(e)}")
            return None
        
        valid_collections = [col.name for col in collections.collections]
        if not valid_collections:
            print("No valid collections found.")
            return None

        # Extract query keywords to improve search relevance
        query_keywords = []
        specific_categories = []
        found_colors = []
        outfit_types = []
        
        if text:
            # Basic tokenization and keyword extraction
            query_lower = text.lower()
            
            # Define direct mappings for common search terms to collections
            direct_mappings = {
                "dress": ["clip_DRESSES_JUMPSUITS"],
                "dresses": ["clip_DRESSES_JUMPSUITS"],
                "jumpsuit": ["clip_DRESSES_JUMPSUITS"],
                "shirt": ["clip_SHIRTS", "clip_men_SHIRTS"],
                "t-shirt": ["clip_men_T-SHIRTS"],
                "tshirt": ["clip_men_T-SHIRTS"],
                "t shirt": ["clip_men_T-SHIRTS"],
                "blazer": ["clip_BLAZERS", "clip_men_BLAZERS"],
                "jacket": ["clip_JACKETS"],
                "trouser": ["clip_men_TROUSERS"],
                "pants": ["clip_men_TROUSERS"],
                "knitwear": ["clip_KNITWEAR"],
                "shoe": ["clip_SHOES", "clip_men_SHOES"],
                "shoes": ["clip_SHOES", "clip_men_SHOES"],
                "shorts": ["clip_men_SHORTS"],
                "hoodie": ["clip_men_HOODIES_SWEATSHIRTS"],
                "sweatshirt": ["clip_men_HOODIES_SWEATSHIRTS"],
                "cardigan": ["clip_men_SWEATERS_CARDIGANS", "clip_KNITWEAR"],
                "sweater": ["clip_men_SWEATERS_CARDIGANS", "clip_KNITWEAR"]
            }
            
            # Check for direct mappings
            for keyword, collections in direct_mappings.items():
                if keyword in query_lower:
                    for collection in collections:
                        if collection in valid_collections and collection not in specific_categories:
                            specific_categories.append(collection)
                    query_keywords.append(keyword)
            
            # IMPORTANT: Extra handling for dresses which seem to be problematic
            if "dress" in query_lower:
                if "clip_DRESSES_JUMPSUITS" in valid_collections:
                    # Triple ensure dress collection is first in the list
                    if "clip_DRESSES_JUMPSUITS" in specific_categories:
                        specific_categories.remove("clip_DRESSES_JUMPSUITS")
                    specific_categories.insert(0, "clip_DRESSES_JUMPSUITS")
                    print("DRESS FOUND IN QUERY - Prioritizing DRESSES_JUMPSUITS collection first")
            
            # Special handling for gender
            is_female_query = False
            if "women" in query_lower or "woman" in query_lower or "female" in query_lower:
                # Prioritize women's collections (those without "men")
                is_female_query = True
                women_collections = [col for col in valid_collections if "men" not in col and any(item in col for item in ["DRESSES", "KNITWEAR", "BLAZERS", "SHIRTS"])]
                for col in women_collections:
                    if col not in specific_categories:
                        specific_categories.append(col)
                query_keywords.append("women")
            
            is_male_query = False
            if "men" in query_lower or "man" in query_lower or "male" in query_lower:
                # Prioritize men's collections
                is_male_query = True
                men_collections = [col for col in valid_collections if "men" in col]
                for col in men_collections:
                    if col not in specific_categories:
                        specific_categories.append(col)
                query_keywords.append("men")
                
            # If no gender is specified but we have items like "dress" that are typically women's,
            # implicitly prioritize women's collections
            if not is_male_query and not is_female_query:
                womens_items = ["dress", "skirt", "blouse", "heels"]
                mens_items = ["tie", "boxer"]
                
                is_implicit_womens = any(item in query_lower for item in womens_items)
                is_implicit_mens = any(item in query_lower for item in mens_items)
                
                if is_implicit_womens:
                    print("Implicitly prioritizing women's collections based on item type")
                    women_collections = [col for col in valid_collections if "men" not in col]
                    for col in women_collections:
                        if col not in specific_categories:
                            specific_categories.append(col)
                elif is_implicit_mens:
                    print("Implicitly prioritizing men's collections based on item type")
                    men_collections = [col for col in valid_collections if "men" in col]
                    for col in men_collections:
                        if col not in specific_categories:
                            specific_categories.append(col)
            
            # Handle colors - extract if present
            enhanced_color_keywords = {
                "red": ["red", "burgundy", "maroon", "crimson", "scarlet"],
                "blue": ["blue", "navy", "azure", "turquoise", "teal", "cyan"],
                "green": ["green", "olive", "lime", "emerald", "sage", "mint"],
                "yellow": ["yellow", "gold", "amber", "mustard"],
                "black": ["black", "jet black", "onyx"],
                "white": ["white", "ivory", "cream", "off-white"],
                "pink": ["pink", "rose", "fuchsia", "magenta"],
                "purple": ["purple", "violet", "lavender", "lilac", "mauve"],
                "orange": ["orange", "coral", "peach", "tangerine"],
                "brown": ["brown", "tan", "beige", "khaki", "camel", "chocolate"],
                "gray": ["gray", "grey", "silver", "charcoal"],
                "multicolor": ["multicolor", "colorful", "patterned", "floral", "striped", "checkered"]
            }
            
            for color, variations in enhanced_color_keywords.items():
                if any(variation in query_lower for variation in variations):
                    found_colors.append(color)
                    query_keywords.append(color)
                    print(f"Detected color: {color}")
            
            outfit_phrases = [
                "outfit", "look", "ensemble", "attire", "full look", 
                "complete outfit", "entire outfit", "full outfit"
            ]
            
            outfit_types_dict = {
                "casual": ["casual", "everyday", "relaxed", "weekend", "comfy"],
                "formal": ["formal", "business", "professional", "office", "work", "elegant"],
                "sporty": ["sporty", "athletic", "workout", "gym", "active", "sport"],
                "party": ["party", "evening", "nightout", "club", "cocktail"],
                "beach": ["beach", "summer", "vacation", "resort"],
                "winter": ["winter", "cold", "snow", "holiday", "christmas"],
                "wedding": ["wedding", "bridal", "ceremony", "special occasion"]
            }
            
            is_outfit_search = any(phrase in query_lower for phrase in outfit_phrases)
            
            if is_outfit_search:
                print("Detected OUTFIT search request")
                query_keywords.append("outfit")
                
                for outfit_type, keywords in outfit_types_dict.items():
                    if any(keyword in query_lower for keyword in keywords):
                        outfit_types.append(outfit_type)
                        print(f"Detected outfit type: {outfit_type}")
        
        print(f"Detected keywords: {query_keywords}")
        print(f"Mapped to specific categories: {specific_categories}")
        print(f"Detected colors: {found_colors}")
        print(f"Outfit types: {outfit_types}")
        
        # Set up prioritized collections - start with specific categories if found
        prioritized_collections = []
        
        # First add specifically identified collections if any
        if specific_categories:
            for category in specific_categories:
                if category in valid_collections and category not in prioritized_collections:
                    prioritized_collections.append(category)
        
        # Then add remaining collections
        for collection in valid_collections:
            if collection not in prioritized_collections:
                prioritized_collections.append(collection)
        
        # Ensure we're not just searching men's blazers by default
        if "clip_men_BLAZERS" in prioritized_collections and prioritized_collections[0] == "clip_men_BLAZERS" and len(prioritized_collections) > 1:
            # If men's blazers is the first in the list but we have other options, deprioritize it
            prioritized_collections.remove("clip_men_BLAZERS")
            prioritized_collections.append("clip_men_BLAZERS")
        
        print(f"Prioritized collection order: {prioritized_collections}")
        
        # Calculate how many results to get per collection
        # If we have specific categories, get more results from those
        if specific_categories:
            results_per_specific = max(3, min(n_results, 5))  # At least 3 results, but no more than 5 or n_results
            results_per_general = 1  # Minimal results from other collections
        else:
            results_per_specific = 0
            results_per_general = max(2, min(n_results // len(prioritized_collections), 3))
        
        if found_colors and not specific_categories:
            results_per_general = 3
        
        all_results = []
        
        # Search across all collections with priority given to more relevant ones
        for collection_name in prioritized_collections:
            try:
                # Use more results for specific categories
                limit = results_per_specific if collection_name in specific_categories else results_per_general
                
                if limit <= 0:
                    continue
                    
                print(f"Searching collection {collection_name} for {limit} results...")
                
                # If this is a specific category we care about, boost the embedding for it
                query_vector = base_query_vector
                if collection_name in specific_categories:
                    query_vector = self._boost_embedding_for_category(base_query_vector, collection_name)
                    print(f"Applied category boosting for {collection_name}")
                
                # Apply color boosting if colors were found but no specific categories
                if found_colors and not specific_categories and len(found_colors) == 1:
                    query_vector = self._boost_embedding_for_color(query_vector, found_colors[0])
                    print(f"Applied color boosting for {found_colors[0]}")
                
                # Apply outfit type boosting if this is an outfit search
                if "outfit" in query_keywords and outfit_types and len(outfit_types) == 1:
                    query_vector = self._boost_embedding_for_outfit(query_vector, outfit_types[0])
                    print(f"Applied outfit boosting for {outfit_types[0]}")
                
                # Use named vector format for beymen collections, regular format for others
                if collection_name.startswith("beymen_"):
                    results = self.client.search(
                        collection_name=collection_name,
                        query_vector={
                            "name": "multimodal",
                            "vector": query_vector
                        },
                        limit=limit,
                        with_payload=True,
                        search_params=models.SearchParams(hnsw_ef=128)
                    )
                else:
                    # For other collections with default vector name
                    results = self.client.search(
                        collection_name=collection_name,
                        query_vector=query_vector,
                        limit=limit,
                        with_payload=True,
                        search_params=models.SearchParams(hnsw_ef=128)
                    )
                
                if results:
                    print(f"Found {len(results)} results in {collection_name}")
                    # Apply score boosting for certain categories
                    for result in results:
                        # If this matches our specific category interest, boost the score
                        if collection_name in specific_categories:
                            # Apply a multiplicative boost (higher is better for results)
                            result.score *= 1.5
                            print(f"Boosted score for result in {collection_name}")
                    
                    all_results.extend([(result, collection_name) for result in results])
                else:
                    print(f"No results found in {collection_name}")
                    
            except Exception as e:
                print(f"Error searching collection {collection_name}: {str(e)}")
                continue
      
        # Sort all results by score (descending, as higher is better)
        sorted_results = sorted(all_results, key=lambda x: x[0].score, reverse=True)
        print(f"Total results found across all collections: {len(sorted_results)}")
        
        # Debug the best results
        if sorted_results:
            print("Top 3 results by score:")
            for i, (result, col) in enumerate(sorted_results[:3]):
                print(f"{i+1}. {col} - {result.payload.get('product_name', 'N/A')} (score: {result.score})")
        
        # Deduplicate and get the top n_results
        final_results = []
        seen_ids = set()
        
        # First, ensure diversity by including at least one item from different categories if possible
        added_categories = set()
        diverse_results = []
        
        # Prioritize specific category results first
        if specific_categories:
            for result, col_name in sorted_results:
                if col_name in specific_categories and col_name not in added_categories:
                    diverse_results.append((result, col_name))
                    added_categories.add(col_name)
                    
                    unique_id = result.payload.get('product_id') or result.id
                    seen_ids.add(unique_id)
                    
                    if len(diverse_results) >= min(n_results, len(specific_categories)):
                        break
            
        # Then add diversity from remaining categories
        for result, col_name in sorted_results:
            if col_name not in added_categories:
                diverse_results.append((result, col_name))
                added_categories.add(col_name)
                
                unique_id = result.payload.get('product_id') or result.id
                seen_ids.add(unique_id)
                
                if len(diverse_results) >= min(n_results, len(prioritized_collections)):
                    break
        
        # Then add remaining results based on score
        for result, col_name in sorted_results:
            unique_id = result.payload.get('product_id') or result.id
            if unique_id not in seen_ids:
                seen_ids.add(unique_id)
                diverse_results.append((result, col_name))
                
            if len(diverse_results) >= n_results:
                break
        
        print(f"Final diverse results: {len(diverse_results)} items from {len(added_categories)} categories")
        for i, (result, col_name) in enumerate(diverse_results):
            print(f"Result {i+1}: {col_name} - {result.payload.get('product_name', 'N/A')}")
            
        return diverse_results


# categoryfree_search = CategoryFreeSearch