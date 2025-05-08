import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TrendFetcher:
    def __init__(self,
                 query: str = "fashion",
                 page_size: int = 10,
                 sources: list = None):
        self.query = query
        self.page_size = page_size
        self.sources = sources or [
            "vogue.com", "www.vogue.com",
            "elle.com", "harpersbazaar.com",
            "cosmopolitan.com", "www.cosmopolitan.com",
            "fashionista.com", "wwd.com",
            "glamour.com", "www.glamour.com",
            "instyle.com", "www.instyle.com",
            "elle.com", "www.elle.com",

        ]
        self.api_key = os.getenv("NEWS_API_KEY")

    def get_current_trends(self) -> str:
        if not self.api_key:
            return "Current trends cannot be retrieved because NEWS_API_KEY is not set."

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.query,
            "qInTitle": self.query,           
            "sortBy": "publishedAt",
            "pageSize": self.page_size,
            "apiKey": self.api_key,
            "domains": ",".join(self.sources),
            "language": "en"
        }

        try:
            response = requests.get(url, params=params)
            print(f"Request URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response payload: {data}")
            response.raise_for_status()

            articles = data.get("articles", [])
            if not articles:
                return ("No current trend articles found from the specified sources. "
                        "Try removing the domains filter or changing your query.")

            STOP_WORDS = {
                "the", "a", "an", "and", "or", "but", "of", "for",
                "on", "in", "with", "to", "by", "at", "from",
                "is", "it"
            }
            keyword_set = set()

            for art in articles:
                title = art.get("title", "")
                tokens = title.lower().strip().split()
                tokens = [t.strip(".,!?;:'\"()[]") for t in tokens]
                for token in tokens:
                    if len(token) > 2 and token not in STOP_WORDS:
                        keyword_set.add(token)

            if keyword_set:
                return ", ".join(sorted(keyword_set))
            else:
                return "No keywords extracted from the fetched articles."

        except requests.HTTPError as http_err:
            msg = data.get("message", str(http_err))
            return f"HTTP error occurred: {msg}"
        except Exception as err:
            return f"Error retrieving current trends: {err}"
        
    def get_image_urls(self) -> str:
        if not self.api_key:
            return "Current trends cannot be retrieved because NEWS_API_KEY is not set."
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.query,
            "qInTitle": self.query,           
            "sortBy": "publishedAt",
            "pageSize": self.page_size,
            "apiKey": self.api_key,
            "domains": ",".join(self.sources),
            "language": "en"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            return [article["urlToImage"] for article in articles if article.get("urlToImage")]
        
        except Exception as err:
            return f"Error retrieving current trends: {err}"
        
        