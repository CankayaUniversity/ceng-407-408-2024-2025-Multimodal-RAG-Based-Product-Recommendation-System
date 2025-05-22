from utils import decode_base64_image
from fashion_search import TextToImageSearch, ImageToImageSearch
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import os

def rag_pipeline(query_text, category, image_base64=None, memory=None):
    """Retrieval-Augmented Generation (RAG) pipeline using LangChain with conversation history."""
    valid_categories = [
        "clip_BASICS", "clip_BLAZERS", "clip_DRESSES_JUMPSUITS", "clip_JACKETS", "clip_KNITWEAR", 
        "clip_men_BLAZERS", "clip_men_HOODIES_SWEATSHIRTS", "clip_men_LINEN", "clip_men_OVERSHIRTS", 
        "clip_men_POLO SHIRTS", "clip_men_SHIRTS", "clip_men_SHOES", "clip_men_SHORTS", 
        "clip_men_SWEATERS_CARDIGANS", "clip_men_T-SHIRTS", "clip_men_TROUSERS", "clip_SHIRTS", 
        "clip_SHOES", "clip_WAISTCOATS_GILETS", "beymen_women_dresses", "beymen_women_jackets",
        "beymen_women_skirts", "beymen_women_sweatshirts", 
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
        You are a personal stylist, helping users to find their needed fashion products.
        You are going to provide personalized fashion recommendations to users.
        Therefore you should only answer fashion based queries, and make suggestions about fashion.
        Do not provide fashion recommendations to queries other than fashion.
        
        Chat history:
        {chat_history}
        
        Based on the following product details:
        {context}
        
        Provide a personalized recommendation with reasoning for a customer interested in '{query_text}'. 
        Use the uploaded image by user in your recommendation, the uploaded image is '{image_base64}'.
        In your response, please include the recommended product's image URL along with the product name and reasoning.
        Keep your response clear and short.
        Make a list of keywords which are relevant to the product and the input query.
        
        If you think the context and the user's query are too irrelevant, do not recommend anything. Only answer the user's input query text.
        """
    )
    
    
    llm = GoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=os.getenv("GOOGLE_API_KEY"))
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    response = chain.run(context=context_str, query_text=query_text, image_base64= image_base64, chat_history=memory)
    
    return response