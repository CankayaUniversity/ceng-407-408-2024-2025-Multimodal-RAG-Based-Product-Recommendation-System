import os
import base64
import requests
from dotenv import load_dotenv
import google.generativeai as genai  


class ImageToTextGenerator:
    def __init__(self, model="gemini-1.5-pro"):
        self.model = genai.GenerativeModel(model)

    def encode_image(self, image_url):
        """Download an image from a URL and encode it in base64."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        except requests.exceptions.RequestException as e:
            print(f"Failed to download the image: {e}")
            return None

    def generate_description(self, image_url, query="Describe this clothing item in extreme detail, including color, fabric, style, and potential use cases."):
        """Generate a text description for an image."""
        image_base64 = self.encode_image(image_url)
        if not image_base64:
            return None


        prompt = query
        image_data = {
            "mime_type": "image/jpeg",
            "data": base64.b64decode(image_base64),
        }


        response = self.model.generate_content(
            contents=[{"text": prompt}, {"inline_data": image_data}]
        )

        return response.text  


if __name__ == "__main__":
    
    load_dotenv()
    GEMINI_API_KEY = os.getenv("gemini_api_key")

    genai.configure(api_key=GEMINI_API_KEY)

    image_url = "https://static.zara.net/photos///2023/I/0/1/p/4968/223/704/2/w/448/4968223704_1_1_1.jpg?ts=1692964746030"
    generator = ImageToTextGenerator()
    description = generator.generate_description(image_url)
    print(description)
