import logging
from services import DatabaseService, ClipEmbeddingService

logger = logging.getLogger(__file__)


def main():
    embedding = ClipEmbeddingService()
    database = DatabaseService(embedding_service=embedding)

    database.initialize_collection()

if __name__ == "__main__":
    main()

    