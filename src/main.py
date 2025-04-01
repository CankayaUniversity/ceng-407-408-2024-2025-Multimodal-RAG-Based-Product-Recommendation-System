import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
#from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from fashion_search.text_to_image import TextToImageSearch  
from fashion_search.image_to_text import ImageToTextGenerator
from fashion_search.image_to_image import ImageToImageSearch

# Load environment variables
load_dotenv()


def rag_pipeline(query_text, image_url=None):
    """Retrieval-Augmented Generation (RAG) pipeline using LangChain."""
    category = "clip_SHIRTS"
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
        In your response, please include the recommended product's image url along with the product name and reasoning.
        """
    )
    
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, google_api_key = GOOGLE_API_KEY)
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(context=context_str, query_text=query_text)
    
    return response

if __name__ == "__main__":
    

    GOOGLE_API_KEY = os.getenv("google_api_key")

    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is missing! Ensure it's set in the .env file.")

    
    query = "i need a summer shirt to wear to work in office. i prefer oversized fit."
    image_url = "https://static.zara.net/photos///2023/I/0/1/p/3564/191/712/2/w/448/3564191712_6_1_1.jpg?ts=1692950069091"
    
    recommendation = rag_pipeline(query, image_url)
    print("Recommendation:\n", recommendation)
