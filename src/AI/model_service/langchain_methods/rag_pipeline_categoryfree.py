from utils import decode_base64_image
from fashion_search import TextToImageSearch, ImageToImageSearch, CategoryFreeSearch
from fashion_trend import TrendFetcher
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import os

def rag_pipeline(query_text, category, image_base64=None, memory=None):
    
    trend_fetcher = TrendFetcher()
    current_trends = trend_fetcher.get_current_trends()
    image_urls = trend_fetcher.get_image_urls()
    
    
    valid_categories = [
        "clip_BASICS", "clip_BLAZERS", "clip_DRESSES_JUMPSUITS", "clip_JACKETS", "clip_KNITWEAR", 
        "clip_men_BLAZERS", "clip_men_HOODIES_SWEATSHIRTS", "clip_men_LINEN", "clip_men_OVERSHIRTS", 
        "clip_men_POLO SHIRTS", "clip_men_SHIRTS", "clip_men_SHOES", "clip_men_SHORTS", 
        "clip_men_SWEATERS_CARDIGANS", "clip_men_T-SHIRTS", "clip_men_TROUSERS", "clip_SHIRTS", 
        "clip_SHOES", "clip_WAISTCOATS_GILETS", 
        "clip_DRESSES", "clip_JACKETS", "clip_SKIRTS", "clip_SWEATSHIRTS", 
        "clip_men_JACKETS", "clip_men_SWEATSHIRTS", "clip_men_SKIRTS", "clip_men_DRESSES","beymen_women_dresses", "beymen_women_jackets",
        "No Category"
    ]
    if category not in valid_categories:
        raise ValueError("Invalid category selected!")
    
    context_parts = []
    original_query = query_text  # Store the original query for reference
    
    if category == "No Category":
        context_parts.append("Retrieved products based on category-free search:")
        try:
            # Extract keywords from query to help guide the category-free search
            query_type = "general"
            query_keywords = []
            common_keywords = {
                "dress": "DRESSES_JUMPSUITS",
                "shirt": "SHIRTS",
                "t-shirt": "T-SHIRTS",
                "blazer": "BLAZERS",
                "jacket": "JACKETS",
                "trouser": "TROUSERS",
                "pant": "TROUSERS",
                "men": "men",
                "women": "women",
                "knitwear": "KNITWEAR",
                "shoe": "SHOES"
            }
            
            # Process query for better understanding
            query_lower = query_text.lower()
            for keyword, category_part in common_keywords.items():
                if keyword in query_lower:
                    query_keywords.append(category_part)
                    
            # Determine if we need to prioritize specific categories based on query
            enhanced_query = query_text
            if query_keywords:
                # If we found relevant keywords, include them in the query for better search
                enhanced_query = f"{query_text} {' '.join(query_keywords)}"
                
            image_input = decode_base64_image(image_base64) if image_base64 else None
            searcher = CategoryFreeSearch() 
            
            # Print what we're searching for
            print(f"Searching for: {enhanced_query} (original: {query_text})")
            
            # Use enhanced query for search
            results = searcher.search(text=enhanced_query, image=image_input, n_results=5)
            
            if results:
                # First, determine what categories were returned
                found_categories = set([col_name for _, col_name in results])
                context_parts.append(f"Found products across {len(found_categories)} different categories: {', '.join(found_categories)}")
                
                # Add the original query for context
                context_parts.append(f"User's original search query: '{original_query}'")
                
                for result, col_name in results:
                    payload = result.payload
                    # Add the category to the product info for better context
                    context_parts.append(
                        f"Product: {payload.get('product_name', 'N/A')} (Category: {col_name.replace('clip_', '')}), "
                        f"Price: {payload.get('price', 'N/A')}, "
                        f"Link: {payload.get('link', 'N/A')}, "
                        f"Image URL: {payload.get('image_url', '')}"
                    )
            else:
                context_parts.append("No products found for the given query.")
        except Exception as e:
            context_parts.append(f"Error during category-free retrieval: {str(e)}")
    else:
        
        text_searcher = TextToImageSearch(collection_name=category)
        text_results = text_searcher.search(query_text, n_results=5)
        context_parts.append("Retrieved products based on the text query:")
        for result in text_results:
            payload = result.payload
            context_parts.append(
                f"Product: {payload.get('product_name', 'N/A')}, "
                f"Price: {payload.get('price', 'N/A')}, "
                f"Link: {payload.get('link', 'N/A')}, "
                f"Image URL: {payload.get('image_url', '')}"
            )
        
        
        if image_base64:
            image = decode_base64_image(image_base64)
            image_searcher = ImageToImageSearch(os.getenv("VECTORDB_URL"), os.getenv("VECTORDB_API"))
            image_results = image_searcher.search(image, category, n_results=5)
            context_parts.append("Retrieved products based on the image query:")
            for result, col_name in image_results:
                payload = result.payload
                context_parts.append(
                    f"Product: {payload.get('product_name', 'N/A')}, "
                    f"Price: {payload.get('price', 'N/A')}, "
                    f"Link: {payload.get('link', 'N/A')}, "
                    f"Image URL: {payload.get('image_url', '')}"
                )
    
    context_str = "\n".join(context_parts)
    
    prompt = PromptTemplate.from_template(
        """
        You are a personal stylist, helping users to find their needed fashion products.
        You are going to provide personalized fashion recommendations to users.
        Therefore you should only answer fashion based queries, and make suggestions about fashion.
        Do not provide fashion recommendations to queries other than fashion.
        
        You are a personal stylist AI assistant, helping users find fashion products they're looking for.
        You must be helpful even when the system doesn't have the exact items the user wants.
        
        Chat history:
        {chat_history}
        
        Based on the following product details:
        {context}
        
        Current Fashion Trends Keywords:
        {trends}
        
        User query: '{query_text}'
        
        IMPORTANT INSTRUCTIONS:
        1. First, analyze what the user is asking for and what products are available.
        2. If we have products that match the user's request (like pink dresses when they ask for a pink dress),
           recommend those directly with enthusiasm.
        3. If we don't have the exact match but have similar or related items, acknowledge this openly:
           "While I don't have the exact [what user asked for], I can recommend some stylish alternatives..."
        4. NEVER say you "cannot fulfill" the request or refuse to help. Always try to be helpful with what's available.
        5. Include product image URLs in your recommendations.
        6. Mention relevant fashion trends that relate to your recommendations.
        7. Be conversational and friendly in your response.
        8. ALWAYS include the product links in your recommendation in this exact format: "Link: [exact product URL]" right after each product.
           This is crucial for the user to be able to buy the product.
        
        Respond with a personalized recommendation that addresses the user's query as best as possible
        with the available products. Make sure to format product links as instructed above.
        """
    )
    
    llm = GoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    response = chain.run(
        context=context_str,
        query_text=query_text,
        image_base64=image_base64,
        trends=current_trends,
        chat_history=memory
    )
    
    return response

