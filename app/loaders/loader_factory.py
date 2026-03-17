import os
from typing import Optional, Type, Dict
from app.core.interfaces import IDocumentLoader
from app.loaders.pdf_loader import PDFLoader
from app.loaders.text_loader import TextLoader
from app.loaders.image_loader import ImageLoader
from app.loaders.audio_loader import AudioLoader

class DocumentLoaderFactory:
    """Factory to create appropriate loader based on file extension."""
    
    _LOADERS: Dict[str, Type[IDocumentLoader]] = {
        ".pdf": PDFLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
        ".png": ImageLoader,
        ".jpg": ImageLoader,
        ".jpeg": ImageLoader,
        ".bmp": ImageLoader,
        ".tiff": ImageLoader,
        ".mp3": AudioLoader,
        ".wav": AudioLoader,
        ".m4a": AudioLoader,
        ".flac": AudioLoader,
        ".ogg": AudioLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str) -> Optional[IDocumentLoader]:
        """Returns a loader instance for the given file path."""
        ext = os.path.splitext(file_path)[1].lower()
        loader_class = cls._LOADERS.get(ext)
        
        if loader_class:
            return loader_class()
            
        raise ValueError(f"No loader found for file extension: {ext}")
