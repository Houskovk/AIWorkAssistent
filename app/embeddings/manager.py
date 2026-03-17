from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config.settings import settings

class EmbeddingManager:
    """Manages embedding models."""
    
    _instance: HuggingFaceEmbeddings = None

    @classmethod
    def get_embedding_function(cls) -> HuggingFaceEmbeddings:
        """Returns the configured embedding function (singleton)."""
        if cls._instance is None:
            cls._instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
        return cls._instance

