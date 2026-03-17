from typing import List
from langchain_community.document_loaders import TextLoader as LangChainTextLoader
from langchain_core.documents import Document
from app.core.interfaces import IDocumentLoader

class TextLoader(IDocumentLoader):
    """Loader for plain text files."""
    
    def load(self, file_path: str) -> List[Document]:
        loader = LangChainTextLoader(file_path, encoding='utf-8')
        return loader.load()

