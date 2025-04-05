from abc import abstractmethod
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        pass

    @abstractmethod
    def image_to_vector(self, image_urls):
        pass

