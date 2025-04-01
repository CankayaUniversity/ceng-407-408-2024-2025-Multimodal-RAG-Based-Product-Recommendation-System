import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from fashion_search.text_to_image import TextToImageSearch  
from fashion_search.image_to_text import ImageToTextGenerator
from fashion_search.image_to_image import ImageToImageSearch

load_dotenv()

def rag_pipeline(query_text, category, image_url=None):
    """Retrieval-Augmented Generation (RAG) pipeline using LangChain."""
    
    if category not in [
        "clip_BASICS", "clip_BLAZERS", "clip_DRESSES_JUMPSUITS", "clip_JACKETS", "clip_KNITWEAR", 
        "clip_men_BLAZERS", "clip_men_HOODIES_SWEATSHIRTS", "clip_men_LINEN", "clip_men_OVERSHIRTS", 
        "clip_men_POLO SHIRTS", "clip_men_SHIRTS", "clip_men_SHOES", "clip_men_SHORTS", 
        "clip_men_SWEATERS_CARDIGANS", "clip_men_T-SHIRTS", "clip_men_TROUSERS", "clip_SHIRTS", 
        "clip_SHOES", "clip_WAISTCOATS_GILETS"
    ]:
        raise ValueError("Invalid category selected!")
    
    
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

    if image_url:
        image_searcher = ImageToImageSearch(os.getenv("qdrant_url"), os.getenv("qdrant_api_key"))
        image_results = image_searcher.search(image_url, category, n_results=5)
        context_parts.append("\nRetrieved products based on the image query:")
        for result, col_name in image_results:
            payload = result.payload
            context_parts.append(
                f"Product: {payload.get('product_name', 'N/A')}, "
                f"Price: {payload.get('price', 'N/A')}, "
                f"Image URL: {payload.get('image_url', '')}"
            )
    
    # Combine context into a single prompt
    context_str = "\n".join(context_parts)
    prompt = PromptTemplate.from_template(
        """
        Based on the following product details:
        {context}
        
        Provide a personalized recommendation with reasoning for a customer interested in '{query_text}'. 
        Use the uploaded image by user in your recommendation, the uploaded image is '{image_url}'.
        In your response, please include the recommended product's image URL along with the product name and reasoning.
        """
    )
    
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(context=context_str, query_text=query_text, image_url=image_url)
    
    return response


if __name__ == "__main__":
    GOOGLE_API_KEY = os.getenv("google_api_key")
    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is missing! Ensure it's set in the .env file.")
    
    query = "I need a dress, in the color of the image I uploaded."
    category = "clip_DRESSES_JUMPSUITS"  
    image_url = "https://www.whitescreen.online/image/red-background.png"
    
    recommendation = rag_pipeline(query, category, image_url)
    print("Recommendation:\n", recommendation)
