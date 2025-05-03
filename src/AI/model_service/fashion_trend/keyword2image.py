import os
import requests
import string
import numpy as np
from sentence_transformers import SentenceTransformer

CATEGORY_KEYWORDS = {
    "Women's Clothing": {"dress", "skirt", "blouse", "top", "fashion", "couture", "women", "style", "elegant", "chic"},
    "Men's Clothing":   {"suit", "shirt", "trousers", "jacket", "men", "casual", "formal", "wear"},
    "Women's Shoes":    {"heels", "flats", "sneakers", "booties", "shoes", "footwear", "women"},
    "Men's Shoes":      {"sneakers", "boots", "loafers", "shoes", "footwear", "men"},
    "Women's Bags":     {"handbag", "tote", "clutch", "purse", "bag", "women"},
    "Men's Bags":       {"briefcase", "backpack", "messenger", "bag", "men"},
    "Women's Accessories": {"scarf", "jewelry", "hat", "belt", "accessory", "women"},
    "Men's Accessories":   {"watch", "belt", "sunglasses", "cap", "accessory", "men"}
}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_HEADERS = {"Authorization": PEXELS_API_KEY}

def fetch_pexels_images(keyword: str, per_page: int = 1) -> list[str]:
    """Return up to `per_page` image URLs for `keyword` from Pexels."""
    url = "https://api.pexels.com/v1/search"
    params = {"query": keyword, "per_page": per_page}
    resp = requests.get(url, headers=PEXELS_HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json().get("photos", [])
    return [photo["src"]["medium"] for photo in data]

class CategoryTrendFetcher:
    def __init__(self, page_size: int = 5, sources: list[str] = None):
        self.page_size = page_size
        self.sources = sources or [
            "vogue.com", "elle.com", "harpersbazaar.com",
            "fashionista.com", "wwd.com"
        ]
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise RuntimeError("Please set NEWS_API_KEY in your environment")

    def get_trends_for_category(self, category: str) -> str:
        if category not in CATEGORY_KEYWORDS:
            raise ValueError(f"Unknown category: {category}")
        query = " OR ".join(CATEGORY_KEYWORDS[category])
        url = "https://newsapi.org/v2/everything"
        params = {
            "q":        query,
            "sortBy":   "publishedAt",
            "pageSize": self.page_size,
            "domains":  ",".join(self.sources),
            "language": "en",
            "apiKey":   self.api_key
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        titles = [art["title"] for art in r.json().get("articles", []) if art.get("title")]
        return ", ".join(titles)

class CategoryTrendKeywordExtractor:
    def __init__(self, raw_trends: str, model_name: str = "paraphrase-MiniLM-L6-v2"):
        self.raw = raw_trends
        self.model = SentenceTransformer(model_name)

    def _parse(self) -> list[str]:
        toks = [t.strip() for t in self.raw.split(",")]
        clean = []
        for t in toks:
            t = t.lower().translate(str.maketrans("", "", string.punctuation))
            if t:
                clean.append(t)
        return clean

    def extract(self, category: str, threshold: float = 0.5) -> list[str]:
        cat_emb = self.model.encode(category)
        out = []
        for tok in self._parse():
            tok_emb = self.model.encode(tok)
            sim = np.dot(tok_emb, cat_emb) / (np.linalg.norm(tok_emb) * np.linalg.norm(cat_emb))
            if sim >= threshold:
                out.append(tok)
        return sorted(set(out))

def main():
    fetcher = CategoryTrendFetcher(page_size=5)
    results: dict[str, str] = {}

    for category in CATEGORY_KEYWORDS:
        raw_trends = fetcher.get_trends_for_category(category)
        extractor = CategoryTrendKeywordExtractor(raw_trends)
        keywords = extractor.extract(category, threshold=0.6)

        search_term = keywords[0] if keywords else category

        try:
            urls = fetch_pexels_images(search_term, per_page=1)
            results[category] = urls[0] if urls else "No image found"
        except Exception as e:
            results[category] = f"Error: {e}"

    for cat, url in results.items():
        print(f"{cat}: {url}")

if __name__ == "__main__":
    main()
