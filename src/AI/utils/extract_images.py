import json

# Function to extract all image URLs from the image data column
def extract_all_images(image_data) -> list:
    try:
        # Convert string to a list of dictionaries
        image_list = json.loads(image_data.replace("'", "\""))  # Fix single-quote issue for JSON parsing
        if isinstance(image_list, list) and len(image_list) > 0:
            return [list(item.keys())[0] for item in image_list]  # Extract all image URLs
    except Exception as e:
        print(f"Error parsing image data: {e}")
    return None