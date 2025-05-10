from typing import Dict, List, Union, Optional, Any
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from .model_service.fashion_search.categoryfree_search import CategoryFreeSearch
from .model_service.langchain_methods.rag_pipeline_categoryfree import rag_pipeline
from .gemini_service import GeminiService
from .vector_data_service import VectorDataService
from .image_processing.feature_extractor import FeatureExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiModalIntegration:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.category_free_search = CategoryFreeSearch()
        self.gemini_service = GeminiService()
        self.vector_data_service = VectorDataService()
        self.feature_extractor = FeatureExtractor()
        
        logger.info("MultiModalIntegration initialized successfully")
    
    async def process_query(self, 
                           query: str, 
                           image_path: Optional[str] = None, 
                           user_id: Optional[str] = None,
                           wardrobe_items: Optional[List[Dict[str, Any]]] = None,
                           style_profile: Optional[Dict[str, Any]] = None,
                           search_type: str = "item",
                           filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a multimodal query using all available RAG components
        
        Args:
            query: Text query from the user
            image_path: Optional path to an image for visual search
            user_id: Optional user ID for personalized results
            wardrobe_items: Optional list of items in user's wardrobe
            style_profile: Optional user style profile for personalization
            search_type: Type of search ("item" or "outfit")
            filters: Optional filters for the search
            
        Returns:
            Dictionary containing search results and recommendations
        """
        logger.info(f"Processing query: '{query}' with search_type: {search_type}")
        
        # Check if the query specifically mentions outfits
        outfit_keywords = ["outfit", "look", "ensemble", "full look", "complete look", 
                          "entire outfit", "full outfit", "wardrobe", "attire"]
        
        # Determine if query explicitly requests an outfit
        query_lower = query.lower()
        explicit_outfit_request = any(keyword in query_lower for keyword in outfit_keywords)
        
        # Only override search_type based on query content when it's explicitly an outfit request
        # IMPORTANT: We never override "outfit" -> "item" automatically, only "item" -> "outfit" when clearly requested
        if explicit_outfit_request and search_type == "item":
            logger.info("Overriding search_type to 'outfit' based on query keywords")
            search_type = "outfit"
        
        try:
            # Step 1: Enhance the query using the RAG pipeline
            enhanced_query = await self._enhance_query(query, user_id, style_profile)
            
            # Step 2: Extract image features if an image is provided
            image_embedding = None
            if image_path:
                image_embedding = await self._process_image(image_path)
            
            # Step 3: Perform category-free search with the enhanced query
            search_results = await self._perform_search(
                enhanced_query, 
                image_embedding, 
                filters, 
                user_id
            )
            
            # Step 4: If outfit search, compose an outfit from search results
            if search_type == "outfit":
                logger.info("Composing outfit based on search results")
                return await self._compose_outfit(
                    query, 
                    search_results, 
                    wardrobe_items, 
                    style_profile,
                    filters
                )
            
            # Step 5: For regular item searches, enhance results with additional metadata and recommendations
            logger.info("Returning individual item search results")
            enhanced_results = await self._enhance_results(
                search_results, 
                query, 
                user_id, 
                style_profile
            )
            
            return {
                "query": query,
                "enhanced_query": enhanced_query,
                "items": enhanced_results,
                "metadata": {
                    "total_results": len(enhanced_results),
                    "search_type": search_type,
                    "filters_applied": filters or {}
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "query": query,
                "items": [],
                "metadata": {
                    "success": False,
                    "message": f"Failed to process query: {str(e)}"
                }
            }
    
    async def _enhance_query(self, 
                            query: str, 
                            user_id: Optional[str] = None,
                            style_profile: Optional[Dict[str, Any]] = None) -> str:
        """Enhance the query using the RAG pipeline"""
        try:
            # Use the RAG pipeline to enhance the query
            enhanced_query = await rag_pipeline(query, user_id=user_id, style_profile=style_profile)
            logger.info(f"Enhanced query: '{query}' → '{enhanced_query}'")
            return enhanced_query
        except Exception as e:
            logger.warning(f"Error enhancing query, using original: {str(e)}")
            return query
    
    async def _process_image(self, image_path: str) -> List[float]:
        """Process an image and extract features"""
        try:
            features = await self.feature_extractor.extract_features(image_path)
            return features
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
    
    async def _perform_search(self, 
                             query: str, 
                             image_embedding: Optional[List[float]] = None,
                             filters: Optional[Dict[str, Any]] = None,
                             user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform a search using the category-free search component"""
        try:
            # Extract any color mentions for color boosting
            colors = []
            if filters and "colors" in filters:
                colors = filters["colors"]
            
            # Extract any category mentions for category boosting
            categories = []
            if filters and "categories" in filters:
                categories = filters["categories"]
            
            # Perform the search with multimodal inputs
            search_results = await self.category_free_search.search(
                query=query,
                image_embedding=image_embedding,
                user_id=user_id,
                colors=colors,
                categories=categories,
                price_range=filters.get("price_range") if filters else None,
                sort_by=filters.get("sort_by") if filters else None,
                page=filters.get("page", 1) if filters else 1,
                page_size=filters.get("page_size", 20) if filters else 20
            )
            
            logger.info(f"Search returned {len(search_results)} results")
            return search_results
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []
    
    async def _compose_outfit(self, 
                             query: str, 
                             search_results: List[Dict[str, Any]],
                             wardrobe_items: Optional[List[Dict[str, Any]]] = None,
                             style_profile: Optional[Dict[str, Any]] = None,
                             filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose an outfit from search results using the Gemini service"""
        try:
            # Extract theme, occasion, and season from query and filters
            theme = query
            occasion = None
            season = None
            color_scheme = None
            
            if filters:
                if "categories" in filters and filters["categories"]:
                    occasion = filters["categories"][0]  # Use first category as occasion
                if "seasons" in filters and filters["seasons"]:
                    season = filters["seasons"][0]  # Use first season
                if "colors" in filters and filters["colors"]:
                    color_scheme = " and ".join(filters["colors"])
            
            # Generate the outfit using Gemini
            outfit = await self.gemini_service.generate_outfit(
                search_results=search_results[:10],  # Top 10 search results
                wardrobe_items=wardrobe_items,
                user_preferences=style_profile,
                theme=theme,
                occasion=occasion,
                season=season,
                color_scheme=color_scheme
            )
            
            return {
                "query": query,
                "outfit": outfit,
                "metadata": {
                    "theme": theme,
                    "occasion": occasion,
                    "season": season,
                    "color_scheme": color_scheme,
                    "total_search_results": len(search_results)
                }
            }
        except Exception as e:
            logger.error(f"Error composing outfit: {str(e)}")
            return {
                "error": str(e),
                "query": query,
                "outfit": {
                    "items": [],
                    "recommendations": []
                },
                "search_items": search_results[:10],  # Return top search results as fallback
                "metadata": {
                    "success": False,
                    "message": f"Failed to compose outfit: {str(e)}"
                }
            }
    
    async def _enhance_results(self, 
                              search_results: List[Dict[str, Any]],
                              query: str,
                              user_id: Optional[str] = None,
                              style_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Enhance search results with additional metadata and recommendations"""
        try:
            if not search_results:
                return []
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor() as executor:
                # Future for getting style recommendations
                style_future = executor.submit(
                    self._get_style_recommendations,
                    search_results,
                    style_profile
                )
                
                # Future for getting similar items
                similar_future = executor.submit(
                    self._get_similar_items,
                    search_results,
                    query
                )
                
                # Wait for futures to complete
                style_recommendations = style_future.result()
                similar_items = similar_future.result()
            
            # Enhance each result with additional metadata
            enhanced_results = []
            for item in search_results:
                enhanced_item = item.copy()
                
                # Add style compatibility score if style profile is available
                if style_profile:
                    enhanced_item["style_compatibility"] = self._calculate_style_compatibility(
                        item, style_profile
                    )
                
                # Add similar items reference
                item_id = item.get("id")
                if item_id and item_id in similar_items:
                    enhanced_item["similar_items"] = [
                        {"id": i["id"], "name": i["name"]} 
                        for i in similar_items[item_id][:3]  # Top 3 similar items
                    ]
                
                enhanced_results.append(enhanced_item)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error enhancing results: {str(e)}")
            return search_results  # Return original results as fallback
    
    def _get_style_recommendations(self, 
                                  search_results: List[Dict[str, Any]],
                                  style_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get style recommendations based on search results and user profile"""
        # This would interact with the recommendation system
        # For now, return a mock response
        return {
            "recommended_styles": ["casual", "minimalist", "streetwear"],
            "color_palette": ["navy", "white", "gray", "black"]
        }
    
    def _get_similar_items(self, 
                          search_results: List[Dict[str, Any]],
                          query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get similar items for each search result"""
        # This would use vector similarity search
        # For now, return empty dict
        return {}
    
    def _calculate_style_compatibility(self, 
                                      item: Dict[str, Any],
                                      style_profile: Dict[str, Any]) -> float:
        """Calculate style compatibility score between an item and user profile"""
        # This would implement a scoring algorithm
        # For now, return a random score between 0.5 and 1.0
        import random
        return round(random.uniform(0.5, 1.0), 2)

# Create a singleton instance for easy import
integration = MultiModalIntegration() 