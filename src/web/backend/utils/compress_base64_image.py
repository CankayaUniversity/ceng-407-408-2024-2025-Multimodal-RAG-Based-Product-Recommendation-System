import io
import base64
from PIL import Image


def compress_base64_image(base64_str, quality=50, max_size=(512, 512)):
    if base64_str is None:
        return None
    
    #base64 to byte
    base, base64_str = base64_str.split(",")
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))

    #resize
    # image_to_encode = image.thumbnail(max_size, Image.Resampling.LANCZOS)
    image = image.resize(max_size, resample=Image.Resampling.LANCZOS)

    #save
    # buffer = io.BytesIO()
    # image.save(buffer, format="JPEG", quality=quality)
    buffer = io.BytesIO()
    format = image.format if image.format else "JPEG"
    image.save(buffer, format=format, quality=quality)
    compressed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    #encode to base64
    
    return f"{base},{compressed_base64}"

