from flask import request, jsonify, current_app
from . import api_blueprint
import jwt
import os
import json
import base64
from models.user_profile import StyleProfile, WardrobeItem
from models.social import Post
from datetime import datetime
import uuid
import tempfile
import requests
import random

# Helper function to verify token
def verify_token(token):
    try:
        response = requests.get("http://localhost:3001/auth/check", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return None

@api_blueprint.route('/outfits/compose', methods=['POST'])
def compose_outfit():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        auth_status = verify_token(token)
        if not auth_status.get('success'):
            return jsonify({"error": auth_status.get('message', 'Authentication failed')}), 401
        
        user_id = auth_status.get('user_id')
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        
        # Extract outfit parameters
        seed_item = data.get('seed_item')
        theme = data.get('theme')
        occasion = data.get('occasion')
        season = data.get('season')
        color_scheme = data.get('color_scheme')
        
        # Ensure at least one parameter is provided
        if not any([seed_item, theme, occasion, season, color_scheme]):
            return jsonify({"error": "At least one parameter (seed_item, theme, occasion, season, or color_scheme) is required"}), 400
        
        # First try to get user preferences
        user_preferences = {}
        try:
            from models.user_profile import StyleProfile
            style_profile = StyleProfile.get_by_user_id(user_id)
            
            if style_profile:
                user_preferences = {
                    'preferred_colors': style_profile.preferred_colors,
                    'preferred_styles': style_profile.preferred_styles,
                    'disliked_colors': style_profile.disliked_colors,
                    'disliked_styles': style_profile.disliked_styles,
                    'occasion_preferences': style_profile.occasion_preferences,
                    'season_preferences': style_profile.season_preferences,
                    'budget_range': style_profile.budget_range
                }
        except Exception as e:
            current_app.logger.warning(f"Error fetching user preferences: {str(e)}")
            
        # Then try to get user's wardrobe items if requested
        wardrobe_items = []
        if data.get('include_wardrobe_items', False):
            try:
                from models.user_profile import WardrobeItem
                user_wardrobe = WardrobeItem.get_user_wardrobe(user_id)
                
                if user_wardrobe:
                    wardrobe_items = [item.to_dict() for item in user_wardrobe]
            except Exception as e:
                current_app.logger.warning(f"Error fetching wardrobe items: {str(e)}")
        
        # Create a search query for category-free search
        search_query = ""
        if theme:
            search_query += f"{theme} "
        if occasion:
            search_query += f"for {occasion} occasion "
        if season:
            search_query += f"for {season} season "
        if color_scheme:
            search_query += f"in {color_scheme} colors "
        if seed_item and seed_item.get('category'):
            search_query += f"to match {seed_item.get('color', '')} {seed_item.get('category', '')} "
            
        search_items = []
        
        # Try to use category-free search first
        if search_query:
            try:
                from fashion_search.categoryfree_search import CategoryFreeSearch
                
                category_free_search = CategoryFreeSearch()
                search_results = category_free_search.search(text=search_query, n_results=15)
                
                if search_results:
                    for result, collection_name in search_results:
                        payload = result.payload
                        # Skip items without necessary information
                        if not payload.get('image_url'):
                            continue
                            
                        search_items.append({
                            'id': payload.get('product_id', str(uuid.uuid4())),
                            'name': payload.get('product_name', 'Unknown Product'),
                            'category': collection_name.replace('clip_', '').replace('men_', "Men's "),
                            'brand': payload.get('brand', 'Unknown'),
                            'color': payload.get('color', 'Unknown'),
                            'image_url': payload.get('image_url'),
                            'price': payload.get('price', 0),
                            'currency': payload.get('currency', 'USD')
                        })
            except Exception as e:
                current_app.logger.warning(f"Error using category-free search: {str(e)}")
        
        # Use Gemini service to generate outfit
        try:
            from gemini_service import GeminiService
            gemini = GeminiService()
            
            # Prepare seed item in the right format if present
            formatted_seed_item = None
            if seed_item:
                formatted_seed_item = {
                    'id': seed_item.get('id'),
                    'name': seed_item.get('name', 'Unknown Item'),
                    'category': seed_item.get('category', 'Unknown'),
                    'color': seed_item.get('color', 'Unknown'),
                    'image_url': seed_item.get('image_url', '')
                }
            
            # Generate outfit using Gemini
            outfit = gemini.generate_outfit(
                user_preferences=user_preferences,
                seed_item=formatted_seed_item,
                theme=theme,
                occasion=occasion,
                season=season,
                color_scheme=color_scheme,
                wardrobe_items=wardrobe_items
            )
            
            # The search_items should be included in the Gemini service during generation
            # Here we add them to the response
            if search_items:
                outfit['search_items'] = search_items
            
            # Generate a unique outfit ID
            outfit_id = str(uuid.uuid4())
            outfit['id'] = outfit_id
            
            return jsonify({
                "success": True,
                "outfit": outfit,
                "message": "Outfit generated successfully"
            })
            
        except Exception as e:
            current_app.logger.error(f"Error generating outfit with Gemini: {str(e)}")
            
            # If Gemini failed but we have search items, return those
            if search_items:
                return jsonify({
                    "success": True,
                    "outfit": {
                        "id": str(uuid.uuid4()),
                        "title": "Recommended Items",
                        "description": f"Here are some items matching your {theme or occasion or season or 'style'} criteria",
                        "items": [
                            {
                                "name": item.get('name'),
                                "category": item.get('category'),
                                "description": f"{item.get('color', 'Stylish')} {item.get('category', 'item')} by {item.get('brand', 'a popular brand')}",
                                "reason": f"This {item.get('category', 'item')} matches your criteria"
                            }
                            for item in search_items[:6]
                        ],
                        "search_items": search_items
                    },
                    "message": "Outfit generated from search results (Gemini service unavailable)"
                })
            
            # If both methods failed, return error
            return jsonify({"error": "Failed to generate outfit", "details": str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in outfit composition: {str(e)}")
        return jsonify({"error": "An error occurred during outfit composition", "details": str(e)}), 500

@api_blueprint.route('/outfits/search', methods=['POST'])
def search_outfits():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        auth_status = verify_token(token)
        if not auth_status.get('success'):
            return jsonify({"error": auth_status.get('message', 'Authentication failed')}), 401
        
        user_id = auth_status.get('user_id')
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        
        query = data.get('query')
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        try:
            # Use category-free search for outfit search
            from fashion_search.categoryfree_search import CategoryFreeSearch
            
            category_free_search = CategoryFreeSearch()
            
            # Modify query to emphasize outfit context
            enhanced_query = f"{query} outfit complete look"
            
            # Use the category-free search
            search_results = category_free_search.search(
                text=enhanced_query,
                n_results=10
            )
            
            # Format results for frontend
            items = []
            if search_results:
                for result, collection_name in search_results:
                    payload = result.payload
                    # Skip items without necessary information
                    if not payload.get('image_url'):
                        continue
                        
                    items.append({
                        'id': payload.get('product_id', str(uuid.uuid4())),
                        'name': payload.get('product_name', 'Unknown Product'),
                        'category': collection_name.replace('clip_', '').replace('men_', "Men's "),
                        'brand': payload.get('brand', 'Unknown'),
                        'color': payload.get('color', 'Unknown'),
                        'price': payload.get('price', 0),
                        'currency': payload.get('currency', 'USD'),
                        'image_url': payload.get('image_url'),
                        'rating': payload.get('rating', 4.5),
                        'description': payload.get('description', 'No description available'),
                        'tags': payload.get('tags', [])
                    })
            
            # Now, if we have enough results, we're done
            if len(items) >= 5:
                return jsonify({
                    "success": True,
                    "items": items,
                    "message": "Search completed successfully"
                })
            
            # If we don't have enough results, try to add some from Gemini
            try:
                from gemini_service import GeminiService
                gemini = GeminiService()
                
                # Generate outfit recommendations based on query
                outfit = gemini.generate_outfit(
                    user_preferences={},
                    theme=query,
                    occasion=None,
                    season=None
                )
                
                if outfit and "items" in outfit:
                    # Add generated outfit items if we don't have enough from search
                    for item in outfit["items"]:
                        # Skip if we already have enough items
                        if len(items) >= 10:
                            break
                            
                        # Generate a mock product from the outfit item
                        items.append({
                            'id': f'gemini-{str(uuid.uuid4())}',
                            'name': item.get('name', 'Recommended Item'),
                            'category': item.get('category', 'Clothing'),
                            'brand': 'AI Recommended',
                            'color': item.get('description', '').split()[0] if item.get('description') else 'Various',
                            'price': random.randint(30, 150),
                            'currency': 'USD',
                            'image_url': f'https://placehold.co/400x500/9CA3AF/FFFFFF?text={item.get("name", "Item").replace(" ", "+")}',
                            'rating': 4.5,
                            'description': item.get('description', 'AI recommended item'),
                            'tags': [query, 'AI recommended']
                        })
            except Exception as e:
                # Log but continue, as we might still have some results from search
                current_app.logger.error(f"Error using Gemini service: {str(e)}")
            
            return jsonify({
                "success": True,
                "items": items,
                "message": "Search completed successfully"
            })
            
        except ImportError:
            # If category-free search is not available, fallback to mock data
            current_app.logger.warning("CategoryFreeSearch not available, using mock data")
            
            items = [
                {
                    'id': f'mock-{i}',
                    'name': f'{query.title()} Style {i+1}',
                    'category': random.choice(['Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Accessories']),
                    'brand': random.choice(['FashionBrand', 'StyleCo', 'TrendyWear', 'ChicStyle']),
                    'color': random.choice(['Black', 'White', 'Blue', 'Red', 'Green', 'Yellow', 'Purple', 'Pink']),
                    'price': random.randint(20, 200),
                    'currency': 'USD',
                    'image_url': f'https://placehold.co/400x500/9CA3AF/FFFFFF?text={query.replace(" ", "+")}+{i+1}',
                    'rating': round(random.uniform(3.5, 5.0), 1),
                    'description': f'A beautiful {query} style item perfect for your wardrobe.',
                    'tags': [query, 'trending', 'recommended']
                }
                for i in range(8)
            ]
            
            return jsonify({
                "success": True,
                "items": items,
                "message": "Search completed with mock data"
            })
            
    except Exception as e:
        current_app.logger.error(f"Error in outfit search: {str(e)}")
        return jsonify({"error": "An error occurred during search", "details": str(e)}), 500

@api_blueprint.route('/outfits/save', methods=['POST'])
def save_outfit():
    """Save a composed outfit to user's collection"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data or 'outfit' not in data:
        return jsonify({"error": "No outfit data provided"}), 400
    
    outfit = data['outfit']
    
    # TODO: Implement saving outfit to database
    # For now, we'll just return success
    
    return jsonify({
        "message": "Outfit saved successfully",
        "data": {
            "outfit_id": str(uuid.uuid4()),
            "saved_at": datetime.now().isoformat()
        }
    })

@api_blueprint.route('/outfits/add-to-wardrobe', methods=['POST'])
def add_outfit_to_wardrobe():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        auth_status = verify_token(token)
        if not auth_status.get('success'):
            return jsonify({"error": auth_status.get('message', 'Authentication failed')}), 401
        
        user_id = auth_status.get('user_id')
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        
        # Check if this is a single item or a complete outfit
        if 'item_id' in data and 'item_details' in data:
            # It's a single item
            item_details = data.get('item_details', {})
            
            # Validate required fields
            if not item_details.get('product_name') or not item_details.get('category'):
                return jsonify({"error": "Product name and category are required for wardrobe items"}), 400
            
            try:
                # Import here to avoid circular imports
                from models.user_profile import WardrobeItem
                
                # Create the wardrobe item
                wardrobe_item = WardrobeItem(
                    user_id=user_id,
                    product_id=item_details.get('product_id', str(uuid.uuid4())),
                    category=item_details.get('category', ''),
                    color=item_details.get('color', ''),
                    style=item_details.get('style', ''),
                    season=item_details.get('season', []),
                    occasions=item_details.get('occasions', []),
                    image_url=item_details.get('image_url', ''),
                    product_name=item_details.get('product_name', ''),
                    custom_name=item_details.get('custom_name', None),
                    purchased_date=item_details.get('purchased_date', None)
                )
                
                # Save the item
                result = wardrobe_item.save()
                
                return jsonify({
                    "success": True,
                    "message": "Item added to wardrobe",
                    "item_id": result
                })
                
            except Exception as e:
                current_app.logger.error(f"Error adding item to wardrobe: {str(e)}")
                return jsonify({"error": "Failed to add item to wardrobe", "details": str(e)}), 500
                
        elif 'outfit_id' in data or 'outfit_items' in data:
            # It's a complete outfit
            outfit_items = data.get('outfit_items', [])
            
            if not outfit_items or not isinstance(outfit_items, list):
                return jsonify({"error": "Outfit items are required and must be a list"}), 400
                
            # Track which items were successfully added
            added_items = []
            failed_items = []
            
            try:
                # Import here to avoid circular imports
                from models.user_profile import WardrobeItem
                
                # Add each outfit item to the wardrobe
                for item in outfit_items:
                    try:
                        # Create the wardrobe item
                        wardrobe_item = WardrobeItem(
                            user_id=user_id,
                            product_id=item.get('id', str(uuid.uuid4())),
                            category=item.get('category', ''),
                            color=item.get('color', ''),
                            style=item.get('style', ''),
                            season=item.get('season', []),
                            occasions=item.get('occasions', []),
                            image_url=item.get('image_url', ''),
                            product_name=item.get('name', ''),
                            custom_name=None,
                            purchased_date=None
                        )
                        
                        # Save the item
                        result = wardrobe_item.save()
                        added_items.append({
                            'id': result,
                            'name': item.get('name', '')
                        })
                        
                    except Exception as e:
                        current_app.logger.error(f"Error adding outfit item to wardrobe: {str(e)}")
                        failed_items.append({
                            'name': item.get('name', ''),
                            'error': str(e)
                        })
                
                return jsonify({
                    "success": True,
                    "message": f"Added {len(added_items)} items to wardrobe, {len(failed_items)} failed",
                    "added_items": added_items,
                    "failed_items": failed_items
                })
                
            except Exception as e:
                current_app.logger.error(f"Error adding outfit to wardrobe: {str(e)}")
                return jsonify({"error": "Failed to add outfit to wardrobe", "details": str(e)}), 500
                
        else:
            return jsonify({"error": "Invalid request: missing item_id/item_details or outfit_items"}), 400
            
    except Exception as e:
        current_app.logger.error(f"Error in add to wardrobe: {str(e)}")
        return jsonify({"error": "An error occurred while adding to wardrobe", "details": str(e)}), 500

@api_blueprint.route('/outfits/share', methods=['POST'])
def share_outfit():
    """Share an outfit to the community feed"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data or 'outfit' not in data:
        return jsonify({"error": "No outfit data provided"}), 400
    
    outfit = data['outfit']
    caption = data.get('caption', f"Check out my {outfit.get('theme', 'new')} outfit!")
    
    # Create a post with the outfit
    post = Post(
        user_id=user_id,
        content=caption,
        title=outfit.get('name', 'My Outfit'),
        image_urls=[item.get('image_url') for item in outfit.get('items', []) if 'image_url' in item],
        outfit_items=outfit.get('items', []),
        tags=['outfit', outfit.get('theme', ''), outfit.get('occasion', '')]
    )
    
    post.save()
    
    return jsonify({
        "message": "Outfit shared successfully",
        "data": post.to_dict()
    })

@api_blueprint.route('/outfits/analyze', methods=['POST'])
def analyze_outfit_image():
    """Analyze an outfit image to identify items and provide styling feedback"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    user_id = payload.get('user_id') or payload.get('email')
    data = request.json
    
    if not data or 'image_data' not in data:
        return jsonify({"error": "No image data provided"}), 400
    
    image_data = data['image_data']
    
    try:
        # TODO: Replace with actual Gemini Vision API call to analyze the image
        # For now, we'll return mock data
        
        # Mock analysis result
        analysis = {
            "identified_items": [
                {
                    "category": "Top",
                    "type": "Button-up Shirt",
                    "color": "Light Blue",
                    "pattern": "Solid",
                    "confidence": 0.92,
                    "bounding_box": {"x1": 0.2, "y1": 0.15, "x2": 0.8, "y2": 0.45}
                },
                {
                    "category": "Bottom",
                    "type": "Chinos",
                    "color": "Beige",
                    "pattern": "Solid",
                    "confidence": 0.89,
                    "bounding_box": {"x1": 0.25, "y1": 0.5, "x2": 0.75, "y2": 0.9}
                },
                {
                    "category": "Footwear",
                    "type": "Sneakers",
                    "color": "White",
                    "pattern": "Solid",
                    "confidence": 0.85,
                    "bounding_box": {"x1": 0.3, "y1": 0.85, "x2": 0.7, "y2": 0.95}
                }
            ],
            "style_assessment": {
                "overall_style": "Smart Casual",
                "color_harmony": "Good - Neutral palette with complementary tones",
                "fit": "Well-fitted",
                "occasion_appropriateness": ["Casual Office", "Weekend Outing", "Casual Dinner"]
            },
            "styling_suggestions": [
                "Consider adding a navy blazer for a more polished look",
                "A leather belt would complement the outfit nicely",
                "Try rolling up the sleeves for a more relaxed vibe"
            ],
            "sustainability_score": 8.5,
            "wardrobe_compatibility": "High - These pieces can mix and match with many other wardrobe items"
        }
        
        return jsonify({
            "message": "Outfit analysis completed",
            "data": analysis
        })
    except Exception as e:
        current_app.logger.error(f"Error analyzing outfit: {str(e)}")
        return jsonify({"error": str(e)}), 500 