import os
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TrendFetcher')

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
        logger.info(f"TrendFetcher initialized with API key: {self.api_key is not None}")

    def fetch_articles(self):
        """
        Fetch fashion articles from NewsAPI
        Returns a list of articles or an empty list if there's an error
        """
        if not self.api_key:
            logger.error("NEWS_API_KEY not set in environment.")
            # Return demo data instead of raising an error
            return self.get_demo_articles()

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
            logger.info(f"Sending request to NewsAPI with params: {params}")
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"NewsAPI returned error: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return self.get_demo_articles()
                
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                logger.warning("No articles returned from NewsAPI")
                return self.get_demo_articles()
                
            logger.info(f"Successfully fetched {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching articles from NewsAPI: {str(e)}")
            return self.get_demo_articles()
    
    def get_demo_articles(self):
        """
        Return hardcoded demo articles when the API is not available
        """
        logger.info("Using demo fashion articles")
        return [
            {
                "title": "Summer Fashion Trends for 2024",
                "description": "Discover the hottest fashion trends for this summer season, from vibrant colors to sustainable fabrics.",
                "url": "https://www.vogue.com/article/summer-fashion-trends-2024",
                "urlToImage": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                "publishedAt": datetime.now().isoformat(),
                "author": "Vogue Fashion Team",
                "source": {"name": "Vogue"}
            },
            {
                "title": "Sustainable Fashion: The Future of Style",
                "description": "How fashion brands are embracing sustainability and eco-friendly practices to reduce their environmental impact.",
                "url": "https://www.elle.com/fashion/sustainable-future",
                "urlToImage": "https://images.unsplash.com/photo-1581784368651-8916092072e8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                "publishedAt": datetime.now().isoformat(),
                "author": "Elle Editorial",
                "source": {"name": "Elle"}
            },
            {
                "title": "Men's Fashion Week: Highlights and Takeaways",
                "description": "The biggest moments and key trends from this year's men's fashion week shows around the world.",
                "url": "https://www.harpersbazaar.com/fashion/mens-fashion-week",
                "urlToImage": "https://images.unsplash.com/photo-1513188732907-5f732b831ca8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                "publishedAt": datetime.now().isoformat(),
                "author": "Harper's Bazaar Staff",
                "source": {"name": "Harper's Bazaar"}
            },
            {
                "title": "Vintage-Inspired Looks Making a Comeback",
                "description": "How designers are drawing inspiration from past decades to create fresh, nostalgic styles for modern fashion lovers.",
                "url": "https://www.fashionista.com/vintage-inspired-trends",
                "urlToImage": "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                "publishedAt": datetime.now().isoformat(),
                "author": "Fashionista Team",
                "source": {"name": "Fashionista"}
            }
        ]
