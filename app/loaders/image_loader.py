from typing import List
import os
import pytesseract
from PIL import Image
from langchain_core.documents import Document
from app.config.settings import settings
from app.core.interfaces import IDocumentLoader

class ImageLoader(IDocumentLoader):
    """Loader for images using pytesseract OCR."""
    
    def __init__(self):
        # Configure tesseract executable path
        if os.path.exists(settings.TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        else:
            print(f"Warning: Tesseract executable not found at {settings.TESSERACT_PATH}")

    def load(self, file_path: str) -> List[Document]:
        try:
            image = Image.open(file_path)
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                print(f"No text found in image: {file_path}")
                return []
                
            # Create a Document
            metadata = {"source": file_path, "type": "image"}
            # Add a prefix to help the LLM know this is OCR content
            content = f"[IMAGE CONTENT FROM: {os.path.basename(file_path)}]\n{text}"
            
            return [Document(page_content=content, metadata=metadata)]
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
            return []

