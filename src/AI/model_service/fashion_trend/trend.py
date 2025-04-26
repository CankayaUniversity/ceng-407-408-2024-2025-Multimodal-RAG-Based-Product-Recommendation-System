import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TrendFetcher:
    def __init__(self, query: str = "fashion trends", page_size: int = 3, source: str = "vogue.com"):
        self.query = query
        self.page_size = page_size
        self.source = source
        self.api_key = os.getenv("NEWS_API_KEY")
    
    def get_current_trends(self) -> str:
        if not self.api_key:
            return "Current trends cannot be retrieved because NEWS_API_KEY is not set."
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.query,
            "sortBy": "publishedAt",
            "pageSize": self.page_size,
            "apiKey": self.api_key,
            "domains": self.source
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            
            if articles:
                STOP_WORDS = {
                    "the", "a", "an", "and", "or", "but", "of", "for", "on", 
                    "in", "with", "to", "by", "at", "from", "is", "it"
                }
                keyword_set = set()
                for art in articles:
                    title = art.get("title", "")
                    tokens = title.lower().strip().split()
                    tokens = [token.strip(".,!?;:'\"()[]") for token in tokens]
                    for token in tokens:
                        if len(token) > 2 and token not in STOP_WORDS:
                            keyword_set.add(token)
                
                if keyword_set:
                    keywords_list = sorted(keyword_set)
                    return ", ".join(keywords_list)
                else:
                    return "No keywords extracted."
            else:
                return "No current trend articles found from the specified source."
        except Exception as e:
            return f"Error retrieving current trends: {str(e)}"
