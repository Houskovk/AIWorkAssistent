from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config.settings import settings
from app.embeddings.manager import EmbeddingManager
from app.core.interfaces import IVectorStore

class ChromaStore(IVectorStore):
    """Implementation of IVectorStore using ChromaDB."""
    
    def __init__(self):
        self.embedding_function = EmbeddingManager.get_embedding_function()
        self.vector_store: Chroma = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=self.embedding_function,
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Adds documents to the ChromaDB vector store."""
        if not documents:
            return
        self.vector_store.add_documents(documents)

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Searches for relevant documents using similarity search."""
        return self.vector_store.similarity_search(query, k=k)

    def clear(self) -> None:
        """Clears the vector store by deleting the collection and recreating it."""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=self.embedding_function,
        )

