import os
import json
import base64
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import requests
from dotenv import load_dotenv
import logging
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service for interacting with Google's Gemini API for fashion AI features
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment variables")
        
        try:
            from fashion_search import CategoryFreeSearch
            self.category_free_search = CategoryFreeSearch()
        except ImportError:
            print("Warning: Could not import CategoryFreeSearch. Some functionality may be limited.")
            self.category_free_search = None
        
        self.gemini_pro_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.gemini_pro_vision_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
    
    def _make_text_request(self, prompt: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to Gemini Pro text model
        """
        default_params = {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 0.8,
            "topK": 40
        }
        
        if parameters:
            default_params.update(parameters)
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": default_params
        }
        
        url = f"{self.gemini_pro_url}?key={self.api_key}"
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Gemini API: {str(e)}")
            return {"error": str(e)}
    
    def _make_vision_request(self, prompt: str, image_data: Union[str, List[str]], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to Gemini Pro Vision model
        image_data can be a single image or list of images in base64 or URL format
        """
        default_params = {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 0.8,
            "topK": 40
        }
        
        if parameters:
            default_params.update(parameters)
        
        # Prepare image parts
        image_parts = []
        if isinstance(image_data, str):
            image_data = [image_data]
        
        for img in image_data:
            if img.startswith('http'):
                # URL image
                image_parts.append({
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": self._download_and_encode_image(img)
                    }
                })
            else:
                # Base64 image
                image_parts.append({
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": img
                    }
                })
        
        # Construct the request
        parts = [{"text": prompt}] + image_parts
        
        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ],
            "generationConfig": default_params
        }
        
        url = f"{self.gemini_pro_vision_url}?key={self.api_key}"
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Gemini Vision API: {str(e)}")
            return {"error": str(e)}
    
    def _download_and_encode_image(self, image_url: str) -> str:
        """
        Download an image from URL and encode it to base64
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(image_url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {str(e)}")
            raise
    
    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract text from Gemini API response
        """
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting text from response: {str(e)}")
            return "Error processing response from Gemini API"
    
    def _extract_json_from_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract JSON data from Gemini API response text
        """
        text = self._extract_text_from_response(response)
        
        # Try to find JSON in the response
        try:
            # Look for JSON patterns
            if "```json" in text and "```" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
            else:
                return {"error": "No JSON found in response", "raw_text": text}
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from response: {str(e)}")
            return {"error": "Invalid JSON in response", "raw_text": text}
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return {"error": str(e), "raw_text": text}
    
    # ===== Fashion AI Feature Methods =====
    
    def generate_outfit(self, 
                        user_preferences: Dict[str, Any], 
                        seed_item: Optional[Dict[str, Any]] = None, 
                        theme: Optional[str] = None,
                        occasion: Optional[str] = None,
                        season: Optional[str] = None,
                        color_scheme: Optional[str] = None,
                        wardrobe_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a complete outfit based on user preferences and constraints
        """
        # First, use category-free search to find relevant items if available
        outfit_items = []
        search_query = ""
        
        # Build a search query based on the input parameters
        if theme:
            search_query += f"{theme} outfit "
        if occasion:
            search_query += f"for {occasion} occasion "
        if season:
            search_query += f"for {season} season "
        if color_scheme:
            search_query += f"in {color_scheme} colors "
            
        # If we have a search query and the CategoryFreeSearch is available, use it
        if search_query and self.category_free_search:
            try:
                # Search for complementary items
                results = self.category_free_search.search(text=search_query, n_results=10)
                
                if results:
                    # Convert search results to outfit items
                    for result, collection in results:
                        payload = result.payload
                        outfit_items.append({
                            "id": payload.get("product_id", str(uuid.uuid4())),
                            "name": payload.get("product_name", "Unknown Product"),
                            "category": collection.replace("clip_", "").replace("men_", "Men's "),
                            "image_url": payload.get("image_url", ""),
                            "price": payload.get("price", 0),
                            "brand": payload.get("brand", "Unknown Brand"),
                            "color": payload.get("color", "Unknown"),
                        })
            except Exception as e:
                print(f"Error using CategoryFreeSearch: {str(e)}")
                # Continue with Gemini-only approach if search fails
                
        # Original Gemini code for outfit generation
        prompt = """
        You are a fashion stylist AI assistant. Please create a complete outfit based on the given parameters.
        
        User preferences:
        {}
        
        {}
        
        {}
        
        {}
        
        {}
        
        {}
        
        {}
        
        Generate a complete outfit with the following information:
        1. A brief title for this outfit
        2. A description of the overall style and look
        3. A list of 4-6 specific clothing and accessory items that compose the outfit
        4. For each item, provide:
           - Item name
           - Item category (top, bottom, shoes, accessory, etc.)
           - A brief description including color, material, style details
           - Why it works in this outfit
        
        Respond with a valid JSON object with these keys:
        - title: string
        - description: string
        - items: array of objects, each with:
          - name: string
          - category: string
          - description: string
          - reason: string
        
        Only return the valid JSON.
        """.format(
            f"Style preferences: {json.dumps(user_preferences, indent=2)}" if user_preferences else "No specific style preferences provided.",
            f"Seed item: {json.dumps(seed_item, indent=2)}" if seed_item else "No seed item provided.",
            f"Theme: {theme}" if theme else "No specific theme provided.",
            f"Occasion: {occasion}" if occasion else "No specific occasion provided.",
            f"Season: {season}" if season else "No specific season provided.",
            f"Color scheme: {color_scheme}" if color_scheme else "No specific color scheme provided.",
            f"Available wardrobe items: {json.dumps(wardrobe_items, indent=2)}" if wardrobe_items else "No existing wardrobe items provided."
        )
        
        # Include the outfit items from category-free search if any
        if outfit_items:
            prompt += f"\n\nConsider using these items that match the criteria:\n{json.dumps(outfit_items, indent=2)}"
            
        parameters = {
            "temperature": 0.7,
            "max_output_tokens": 1024,
            "top_p": 0.8,
            "top_k": 40
        }
        
        response = self._make_text_request(prompt, parameters)
        outfit_json = self._extract_json_from_response(response)
        
        # Add a source field to the result indicating if items came from search
        if outfit_items:
            outfit_json["search_items"] = outfit_items[:5]  # Include up to 5 search results
            
        return outfit_json

# Example usage
if __name__ == "__main__":
    gemini_service = GeminiService()
    
    # Test the outfit generation
    outfit = gemini_service.generate_outfit(
        user_preferences={
            "preferred_colors": ["blue", "black", "white"],
            "preferred_styles": ["casual", "minimalist"],
            "disliked_colors": ["yellow", "orange"],
            "disliked_styles": ["boho", "flashy"]
        },
        theme="Business casual",
        occasion="Office meeting",
        season="Fall"
    )
    
    print(json.dumps(outfit, indent=2)) 