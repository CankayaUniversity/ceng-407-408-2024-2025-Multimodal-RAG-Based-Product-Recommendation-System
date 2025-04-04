from PIL import Image
import base64
import io

def decode_base64_image(image_base64: str) -> Image.Image:
    """Decode a base 64 encoded image string and return Pil iamge object"""
    image_base64 = image_base64.split(",")[1]
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    return image