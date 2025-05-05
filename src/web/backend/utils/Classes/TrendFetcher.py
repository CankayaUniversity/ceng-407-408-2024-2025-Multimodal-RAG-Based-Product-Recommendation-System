import os
import requests
from dotenv import load_dotenv

from datetime import datetime

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
            "fashionista.com", "wwd.com"
        ]
        self.api_key = os.getenv("NEWS_API_KEY")

    def fetch_articles(self):
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not set in environment.")

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

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
