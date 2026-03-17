from typing import List
from langchain_community.document_loaders import PyPDFLoader as LangChainPyPDFLoader
from langchain_core.documents import Document
from app.core.interfaces import IDocumentLoader

class PDFLoader(IDocumentLoader):
    """Loader for PDF files using pypdf."""
    
    def load(self, file_path: str) -> List[Document]:
        loader = LangChainPyPDFLoader(file_path)
        return loader.load()

