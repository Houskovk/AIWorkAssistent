from abc import ABC, abstractmethod
from typing import List, Generator, Any, Optional, Dict
from langchain_core.documents import Document

class IDocumentLoader(ABC):
    """Interface for document loaders."""
    
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """Loads a document from a file path."""
        pass

class IEmbeddingModel(ABC):
    """Interface for embedding models."""
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single string."""
        pass
    
    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of strings."""
        pass

class IVectorStore(ABC):
    """Interface for vector store operations."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Adds documents to the vector store."""
        pass
        
    @abstractmethod
    def search(self, query: str, k: int = 4) -> List[Document]:
        """searches for relevant documents."""
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """Clears all data from the vector store."""
        pass

class ILLMClient(ABC):
    """Interface for LLM interaction."""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: Optional[str] = None, history: List[Dict[str, str]] = None) -> Generator[str, None, None]:
        """Generates a streaming response from the LLM."""
        pass
        
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates a non-streaming string response from the LLM."""
        pass
