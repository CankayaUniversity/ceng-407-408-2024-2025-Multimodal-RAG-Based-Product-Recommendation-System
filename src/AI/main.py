import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from fashion_search.text_to_image import TextToImageSearch  
from fashion_search.image_to_text import ImageToTextGenerator
from fashion_search.image_to_image import ImageToImageSearch
import io
from PIL import Image
import base64
from time import sleep


load_dotenv()


def decode_base64_image(image_base64: str) -> Image.Image:
    """Decode a base 64 encoded image string and return Pil iamge object"""
    image_base64 = image_base64.split(",")[1]
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    return image


def rag_pipeline(query_text, category, image_base64=None, memory=None):
    """Retrieval-Augmented Generation (RAG) pipeline using LangChain with conversation history."""
    valid_categories = [
        "clip_BASICS", "clip_BLAZERS", "clip_DRESSES_JUMPSUITS", "clip_JACKETS", "clip_KNITWEAR", 
        "clip_men_BLAZERS", "clip_men_HOODIES_SWEATSHIRTS", "clip_men_LINEN", "clip_men_OVERSHIRTS", 
        "clip_men_POLO SHIRTS", "clip_men_SHIRTS", "clip_men_SHOES", "clip_men_SHORTS", 
        "clip_men_SWEATERS_CARDIGANS", "clip_men_T-SHIRTS", "clip_men_TROUSERS", "clip_SHIRTS", 
        "clip_SHOES", "clip_WAISTCOATS_GILETS"
    ]
    if category not in valid_categories:
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


    if image_base64:
        
        image = decode_base64_image(image_base64)
        
        image_searcher = ImageToImageSearch(os.getenv("VECTORDB_URL"), os.getenv("VECTORDB_API"))
        image_results = image_searcher.search(image, category, n_results=5)
        context_parts.append("\nRetrieved products based on the image query:")
        for result, col_name in image_results:
            payload = result.payload
            context_parts.append(
                f"Product: {payload.get('product_name', 'N/A')}, "
                f"Price: {payload.get('price', 'N/A')}, "
                f"Image URL: {payload.get('image_url', '')}"
            )


    context_str = "\n".join(context_parts)
    
    prompt = PromptTemplate.from_template(
        """
        Chat history:
        {chat_history}
        
        Based on the following product details:
        {context}
        
        Provide a personalized recommendation with reasoning for a customer interested in '{query_text}'. 
        Use the uploaded image by user in your recommendation, the uploaded image is '{image_base64}'.
        In your response, please include the recommended product's image URL along with the product name and reasoning.
        """
    )
    
    
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    response = chain.run(context=context_str, query_text=query_text, image_base64= image_base64)
    
    return response


if __name__ == "__main__":
    
    GOOGLE_API_KEY = os.getenv("google_api_key")
    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is missing! Ensure it's set in the .env file.")
    

    memory = ConversationBufferMemory(memory_key="chat_history", input_key="query_text", return_messages=True)
    

    query = "I need a yellow dress for a summer night out. It should have floral prints. Please consider the uploaded image as well."
    category = "clip_DRESSES_JUMPSUITS"  
    
    f = open("ornek.txt", "r")
    image_base64 = f.readline()
    print(image_base64)
    
    
    recommendation = rag_pipeline(query, category, image_base64, memory)
    print("Recommendation:\n", recommendation)
    
    
    sleep(60)
    
    #   follow-up query with chat history included
    followup_query = "I liked that suggestion, but can you recommend a piece with more flowers?"
    followup_recommendation = rag_pipeline(followup_query, category, image_base64, memory)
    print("Follow-up Recommendation:\n", followup_recommendation)
