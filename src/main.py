import os
import base64
import requests
from dotenv import load_dotenv
import google.generativeai as genai  

from fashion_search.text_to_image import TextToImageSearch  
from fashion_search.image_to_text import ImageToTextGenerator
from fashion_search.image_to_image import ImageToImageSearch




def rag_pipeline(query_text, image_url=None):
    #text based search
    text_searcher = TextToImageSearch(collection_name=category) 
    text_results = text_searcher.search(query_text, n_results=5)


    context_parts = ["Retrieved products based on the text query:"]
    for result in text_results:
        payload = result.payload
        context_parts.append(
            f"Product: {payload.get('product_name', 'N/A')}, "
            f"Price: {payload.get('price', 'N/A')}, "
            f"Image URL: {payload.get('image_url', '')}"
        )

    # image-based search if there is image input
    if image_url:
        qdrant_url = os.getenv("qdrant_url")
        api_key = os.getenv("qdrant_api_key")
        image_searcher = ImageToImageSearch(qdrant_url, api_key)
        image_results = image_searcher.search(image_url, category, n_results=5)
        
        context_parts.append("\nRetrieved products based on the image query:")
        for result, col_name in image_results:
            payload = result.payload
            context_parts.append(
                f"Product: {payload.get('product_name', 'N/A')}, "
                f"Price: {payload.get('price', 'N/A')}, "
                f"Image URL: {payload.get('image_url', '')}"
            )
    
    #context combining into a single prompt for the LLM
    context_str = "\n".join(context_parts)
    prompt = (
        f"Based on the following product details:\n{context_str}\n\n"
        f"Provide a personalized recommendation with reasoning for a customer interested in '{query_text}'."
    )
    
    
    generator = ImageToTextGenerator(model="gemini-1.5-pro")
    response = generator.model.generate_content(contents=[{"text": prompt}])
    return response.text



if __name__ == "__main__":
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv("gemini_api_key")
    genai.configure(api_key=GEMINI_API_KEY)
    
    
    query = "i need a long, chic dress to wear to a dinner date. i prefer shiny fabric."

    image_url = "https://static.zara.net/photos///2023/I/0/1/p/8490/899/690/2/w/448/8490899690_1_1_1.jpg?ts=1692879490213"
    
    category = "clip_DRESSES_JUMPSUITS"
    
    
    
    recommendation = rag_pipeline(query, image_url)
    print("Recommendation:\n", recommendation)
    