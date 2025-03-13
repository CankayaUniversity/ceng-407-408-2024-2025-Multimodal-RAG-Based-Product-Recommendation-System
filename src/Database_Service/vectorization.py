
from sentence_transformers import SentenceTransformer
import requests
from PIL import Image
import io
import numpy as np

# load CLIP model
model = SentenceTransformer('clip-ViT-B-32')

# Function to get image vectors for all images
def images_to_vectors(image_urls):
    vectors = []
    valid_urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for url in image_urls:
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content)).convert("RGB")
                image = image.resize((224, 224)) #resize images
                vector = model.encode(image)
                vectors.append(vector)
                valid_urls.append(url)
                print("success")
            else:
                print(f"Failed to fetch image: {url}")
        except Exception as e:
            print(f"Error processing image {url}: {e}")

    if vectors:
        return np.mean(vectors, axis=0), valid_urls  # Average vector for multiple images
    return None