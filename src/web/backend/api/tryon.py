from flask import request, jsonify, current_app
import requests
import os
import base64
from io import BytesIO
from dotenv import load_dotenv
from . import api_blueprint
import uuid
import tempfile
import json
import re

# Load environment variables
load_dotenv()

@api_blueprint.route('/tryon', methods=['POST'])
def try_on():
    """
    API endpoint for virtual try-on feature using RapidAPI's try-on-diffusion API.
    Accepts both URL-based images and file uploads.
    """
    try:
        # Get RapidAPI key from environment
        api_key = os.getenv('RAPIDAPI_KEY')
        if not api_key:
            return jsonify({"error": "RapidAPI key not found in environment"}), 500

        # Check if request contains files or URLs
        data = request.form.to_dict()
        files = request.files
        
        avatar_path = None
        clothing_path = None
        
        try:
            # Process request based on input type (URL, file, or base64)
            if 'avatar_image' in files and 'clothing_image' in files:
                # File-based request
                avatar_file = files['avatar_image']
                clothing_file = files['clothing_image']
                
                # Call the file-based API
                result = try_on_with_files(avatar_file, clothing_file, api_key)
                return jsonify(result)
                
            elif 'avatar_image_url' in data and 'clothing_image_url' in data:
                avatar_url = data.get('avatar_image_url')
                clothing_url = data.get('clothing_image_url')
                
                # Check if the avatar is a base64 encoded image
                is_avatar_base64 = avatar_url.startswith('data:image')
                # Check if the clothing is a base64 encoded image
                is_clothing_base64 = clothing_url.startswith('data:image')
                
                # Both are base64 images
                if is_avatar_base64 and is_clothing_base64:
                    # Create temp files from base64 data
                    temp_dir = tempfile.gettempdir()
                    
                    # Process avatar image
                    try:
                        avatar_data = re.sub('^data:image/.+;base64,', '', avatar_url)
                        avatar_binary = base64.b64decode(avatar_data)
                        avatar_name = f"{uuid.uuid4()}.jpg"
                        avatar_path = os.path.join(temp_dir, avatar_name)
                        
                        with open(avatar_path, 'wb') as f:
                            f.write(avatar_binary)
                        
                        # Process clothing image
                        clothing_data = re.sub('^data:image/.+;base64,', '', clothing_url)
                        clothing_binary = base64.b64decode(clothing_data)
                        clothing_name = f"{uuid.uuid4()}.jpg"
                        clothing_path = os.path.join(temp_dir, clothing_name)
                        
                        with open(clothing_path, 'wb') as f:
                            f.write(clothing_binary)
                        
                        # Use the file-based API since we've converted to files
                        result = try_on_with_temp_files(avatar_path, clothing_path, api_key)
                        return jsonify(result)
                    except Exception as e:
                        return jsonify({"error": f"Failed to process base64 images: {str(e)}"}), 400
                
                # Avatar is base64, clothing is URL
                elif is_avatar_base64 and not is_clothing_base64:
                    # Create temp file for avatar
                    temp_dir = tempfile.gettempdir()
                    
                    try:
                        # Process avatar image from base64
                        avatar_data = re.sub('^data:image/.+;base64,', '', avatar_url)
                        avatar_binary = base64.b64decode(avatar_data)
                        avatar_name = f"{uuid.uuid4()}.jpg"
                        avatar_path = os.path.join(temp_dir, avatar_name)
                        
                        with open(avatar_path, 'wb') as f:
                            f.write(avatar_binary)
                        
                        # Download the clothing image from URL
                        try:
                            clothing_binary = download_image_from_url(clothing_url)
                            clothing_name = f"{uuid.uuid4()}.jpg"
                            clothing_path = os.path.join(temp_dir, clothing_name)
                            
                            with open(clothing_path, 'wb') as f:
                                f.write(clothing_binary)
                        except Exception as e:
                            return jsonify({"error": f"Failed to download clothing image: {str(e)}"}), 400
                        
                        # Use the file-based API with both files
                        result = try_on_with_temp_files(avatar_path, clothing_path, api_key)
                        return jsonify(result)
                    except Exception as e:
                        return jsonify({"error": f"Failed to process mixed format images: {str(e)}"}), 400
                
                # Both are URLs
                elif not is_avatar_base64 and not is_clothing_base64:
                    result = try_on_with_url(avatar_url, clothing_url, api_key)
                    return jsonify(result)
                
                # Avatar is URL, clothing is base64
                elif not is_avatar_base64 and is_clothing_base64:
                    # Create temp file for clothing
                    temp_dir = tempfile.gettempdir()
                    
                    try:
                        # Download the avatar image from URL
                        try:
                            avatar_binary = download_image_from_url(avatar_url)
                            avatar_name = f"{uuid.uuid4()}.jpg"
                            avatar_path = os.path.join(temp_dir, avatar_name)
                            
                            with open(avatar_path, 'wb') as f:
                                f.write(avatar_binary)
                        except Exception as e:
                            return jsonify({"error": f"Failed to download avatar image: {str(e)}"}), 400
                        
                        # Process clothing image from base64
                        clothing_data = re.sub('^data:image/.+;base64,', '', clothing_url)
                        clothing_binary = base64.b64decode(clothing_data)
                        clothing_name = f"{uuid.uuid4()}.jpg"
                        clothing_path = os.path.join(temp_dir, clothing_name)
                        
                        with open(clothing_path, 'wb') as f:
                            f.write(clothing_binary)
                        
                        # Use the file-based API with both files
                        result = try_on_with_temp_files(avatar_path, clothing_path, api_key)
                        return jsonify(result)
                    except Exception as e:
                        return jsonify({"error": f"Failed to process mixed format images: {str(e)}"}), 400
                
                else:
                    return jsonify({
                        "error": "Invalid URL format. URLs must be either web URLs or properly formatted base64 images."
                    }), 400
                
            else:
                return jsonify({
                    "error": "Invalid request. Provide either both 'avatar_image_url' and 'clothing_image_url' OR both 'avatar_image' and 'clothing_image' files."
                }), 400
                
        finally:
            # Clean up temporary files
            if avatar_path and os.path.exists(avatar_path):
                os.remove(avatar_path)
            if clothing_path and os.path.exists(clothing_path):
                os.remove(clothing_path)
                
    except Exception as e:
        current_app.logger.error(f"Try-on API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def try_on_with_url(avatar_url, clothing_url, api_key):
    """
    Function to handle try-on with image URLs
    """
    url = "https://try-on-diffusion.p.rapidapi.com/try-on-url"
    
    # Fix for Zara URLs with multiple slashes
    # Normalize clothing_url if it's a Zara URL - they often have triple slashes that need special handling
    if "zara.net" in clothing_url:
        # Clean up the URL to ensure proper encoding
        clothing_url = clothing_url.replace('///', '/')
        if '://' in clothing_url:
            protocol, rest = clothing_url.split('://', 1)
            clothing_url = f"{protocol}://{rest.replace('//', '/')}"
    
    payload = {
        "avatar_image_url": avatar_url,
        "clothing_image_url": clothing_url
    }
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Sending request to RapidAPI with clothing URL: {clothing_url}")

    try:
        response = requests.post(url, data=payload, headers=headers)
        
        # Check if response is successful
        if response.status_code != 200:
            error_message = f"RapidAPI Error: {response.status_code}"
            try:
                error_data = response.json()
                error_message = f"{error_message} - {json.dumps(error_data)}"
            except:
                error_message = f"{error_message} - {response.text}"
            
            return {"error": error_message}
        
        # Try to parse JSON response
        try:
            result = response.json()
            return result
        except ValueError:
            # Response is image data
            img_data = response.content
            # Convert image to base64 for easy transmission
            base64_img = base64.b64encode(img_data).decode('utf-8')
            return {
                "success": True,
                "image": base64_img,
                "content_type": response.headers.get("Content-Type", "image/png")
            }
    except Exception as e:
        print(f"Error in try_on_with_url: {str(e)}")
        return {"error": f"Error accessing image URLs: {str(e)}"}

def try_on_with_temp_files(avatar_path, clothing_path, api_key):
    """
    Function to handle try-on with temporary image files
    """
    url = "https://try-on-diffusion.p.rapidapi.com/try-on-file"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com"
    }
    
    try:
        files = {
            "avatar_image": (os.path.basename(avatar_path), open(avatar_path, 'rb'), "image/jpeg"),
            "clothing_image": (os.path.basename(clothing_path), open(clothing_path, 'rb'), "image/jpeg")
        }
        
        response = requests.post(url, files=files, headers=headers)
        
        # Check if response is successful
        if response.status_code != 200:
            error_message = f"RapidAPI Error: {response.status_code}"
            try:
                error_data = response.json()
                error_message = f"{error_message} - {json.dumps(error_data)}"
            except:
                error_message = f"{error_message} - {response.text}"
            
            return {"error": error_message}
        
        # Try to parse JSON response
        try:
            result = response.json()
            return result
        except ValueError:
            # Response is image data
            img_data = response.content
            # Convert image to base64 for easy transmission
            base64_img = base64.b64encode(img_data).decode('utf-8')
            return {
                "success": True,
                "image": base64_img,
                "content_type": response.headers.get("Content-Type", "image/png")
            }
    except Exception as e:
        current_app.logger.error(f"Error processing files: {str(e)}")
        return {"error": f"Error processing files: {str(e)}"}

def try_on_with_files(avatar_file, clothing_file, api_key):
    """
    Function to handle try-on with image files
    """
    # Save files to temp directory
    avatar_path = None
    clothing_path = None
    
    try:
        # Create temp files
        avatar_name = f"{uuid.uuid4()}.{avatar_file.filename.split('.')[-1]}"
        clothing_name = f"{uuid.uuid4()}.{clothing_file.filename.split('.')[-1]}"
        
        # Save the uploaded files temporarily
        temp_dir = tempfile.gettempdir()
        avatar_path = os.path.join(temp_dir, avatar_name)
        clothing_path = os.path.join(temp_dir, clothing_name)
        
        avatar_file.save(avatar_path)
        clothing_file.save(clothing_path)
        
        return try_on_with_temp_files(avatar_path, clothing_path, api_key)
            
    except Exception as e:
        raise e
    finally:
        # Clean up temporary files
        if avatar_path and os.path.exists(avatar_path):
            os.remove(avatar_path)
        if clothing_path and os.path.exists(clothing_path):
            os.remove(clothing_path)

# For mixed format requests where clothing image is a URL, let's implement a helper function to download it first
def download_image_from_url(image_url):
    """Download an image from URL and return as binary data"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Fix for Zara URLs with multiple slashes
    if "zara.net" in image_url:
        # Clean up the URL to ensure proper encoding
        image_url = image_url.replace('///', '/')
        if '://' in image_url:
            protocol, rest = image_url.split('://', 1)
            image_url = f"{protocol}://{rest.replace('//', '/')}"
    
    print(f"Downloading image from URL: {image_url}")
    
    try:
        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Check if the response is actually an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"Warning: Content-Type is not an image: {content_type}")
        
        return response.content
    except Exception as e:
        print(f"Error downloading image from {image_url}: {str(e)}")
        raise ValueError(f"Failed to download image from URL: {image_url}. Error: {str(e)}") 