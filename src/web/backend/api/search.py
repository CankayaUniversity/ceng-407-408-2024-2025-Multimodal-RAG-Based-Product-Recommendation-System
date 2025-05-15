from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Header, Query
import os
import tempfile
import logging
import json
from datetime import datetime

from pydantic import BaseModel

from src.AI.multimodal_integration import integration
from .auth import verify_token, get_user_id
from src.web.backend.models.style_profile import StyleProfile

router = APIRouter()
logger = logging.getLogger(__name__)

class SearchQuery(BaseModel):
    query: str
    user_id: Optional[str] = None
    include_style_profile: Optional[bool] = False
    search_type: Optional[str] = "item"  # "item" or "outfit"
    filters: Optional[Dict[str, Any]] = None

class SearchImageQuery(BaseModel):
    caption: Optional[str] = ""
    user_id: Optional[str] = None
    include_style_profile: Optional[bool] = False
    search_type: Optional[str] = "item"  # "item" or "outfit"
    filters: Optional[Dict[str, Any]] = None

@router.post("/search")
async def search(
    search_request: SearchQuery,
    authorization: Optional[str] = Header(None)
):
    """
    Search for fashion items or outfits using text query
    """
    try:
        # Verify user token if provided
        user_id = None
        if authorization:
            token = authorization.replace("Bearer ", "")
            try:
                user_data = await verify_token(token)
                user_id = user_data.get("user_id")
            except Exception as e:
                logger.warning(f"Token verification failed: {str(e)}")
        
        # Override user_id if provided in request
        if search_request.user_id:
            user_id = search_request.user_id
        
        # Get user's style profile if requested
        style_profile = None
        if user_id and search_request.include_style_profile:
            style_profile = await StyleProfile.get_by_user_id(user_id)
        
        # Process the query using our integrated multimodal system
        results = await integration.process_query(
            query=search_request.query,
            user_id=user_id,
            wardrobe_items=None,  # Wardrobe feature disabled
            style_profile=style_profile,
            search_type=search_request.search_type,
            filters=search_request.filters
        )
        
        # Log the search for analytics
        logger.info(f"Search request: '{search_request.query}' by user: {user_id}, type: {search_request.search_type}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/image-search")
async def image_search(
    image: UploadFile = File(...),
    caption: str = Form(""),
    include_style_profile: bool = Form(False),
    search_type: str = Form("item"),
    filters: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None)
):
    """
    Search for fashion items or outfits using image
    """
    try:
        # Save the uploaded image to a temporary file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"search_image_{timestamp}_{image.filename}"
        image_path = os.path.join(temp_dir, image_filename)
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Verify user token if provided
        user_id = None
        if authorization:
            token = authorization.replace("Bearer ", "")
            try:
                user_data = await verify_token(token)
                user_id = user_data.get("user_id")
            except Exception as e:
                logger.warning(f"Token verification failed: {str(e)}")
        
        # Parse filters if provided
        parsed_filters = None
        if filters:
            try:
                parsed_filters = json.loads(filters)
            except:
                logger.warning("Failed to parse filters JSON, ignoring filters")
        
        # Get user's style profile if requested
        style_profile = None
        if user_id and include_style_profile:
            style_profile = await StyleProfile.get_by_user_id(user_id)
        
        # Process the query using our integrated multimodal system
        results = await integration.process_query(
            query=caption,
            image_path=image_path,
            user_id=user_id,
            wardrobe_items=None,  # Wardrobe feature disabled
            style_profile=style_profile,
            search_type=search_type,
            filters=parsed_filters
        )
        
        # Clean up temporary file
        try:
            os.remove(image_path)
        except:
            pass
        
        # Log the search for analytics
        logger.info(f"Image search with caption: '{caption}' by user: {user_id}, type: {search_type}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error processing image search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image search failed: {str(e)}")

@router.get("/trending")
async def get_trending_items(
    category: Optional[str] = Query(None),
    limit: int = Query(10),
    authorization: Optional[str] = Header(None)
):
    """
    Get trending fashion items across the platform or in a specific category
    """
    try:
        # Verify user token if provided (optional for this endpoint)
        user_id = None
        if authorization:
            token = authorization.replace("Bearer ", "")
            try:
                user_data = await verify_token(token)
                user_id = user_data.get("user_id")
            except Exception as e:
                logger.warning(f"Token verification failed: {str(e)}")
        
        # For now, return mock trending data
        trending_items = [
            {
                "id": f"item_{i}",
                "name": f"Trending Item {i}",
                "brand": f"Brand {i % 5 + 1}",
                "category": category or f"Category {i % 7 + 1}",
                "color": f"Color {i % 8 + 1}",
                "price": 50 + (i * 10),
                "currency": "USD",
                "rating": 4.0 + (i % 10) / 10,
                "image_url": f"https://placehold.co/300x400/9CA3AF/FFFFFF?text=Trending+{i}",
                "trending_score": 90 - (i * 3),
                "trending_days": i % 5 + 1
            }
            for i in range(limit)
        ]
        
        # Filter by category if provided
        if category:
            trending_items = [item for item in trending_items if item["category"].lower() == category.lower()]
        
        return {
            "items": trending_items,
            "metadata": {
                "total": len(trending_items),
                "category": category,
                "query_time": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching trending items: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get trending items: {str(e)}")

@router.get("/recommendations")
async def get_personalized_recommendations(
    limit: int = Query(10),
    context: Optional[str] = Query(None),  # can be "home", "style"
    authorization: Optional[str] = Header(None)
):
    """
    Get personalized fashion recommendations for a user
    """
    try:
        # This endpoint requires authentication
        if not authorization:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        token = authorization.replace("Bearer ", "")
        try:
            user_data = await verify_token(token)
            user_id = user_data.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
        
        # Get user's style profile
        style_profile = await StyleProfile.get_by_user_id(user_id)
        
        # Use the Gemini service to generate recommendations
        from src.AI.gemini_service import GeminiService
        gemini = GeminiService()
        
        recommendations = await gemini.generate_recommendations(
            user_id=user_id,
            user_preferences=style_profile,
            wardrobe_items=None,  # Wardrobe feature disabled
            context=context,
            limit=limit
        )
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}") 