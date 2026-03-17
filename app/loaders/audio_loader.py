from typing import List
from langchain_core.documents import Document
from app.core.interfaces import IDocumentLoader
from app.audio.manager import audio_manager

class AudioLoader(IDocumentLoader):
    """Loader for audio files (mp3, wav, m4a)."""
    
    def load(self, file_path: str) -> List[Document]:
        """
        Transcribes audio file to text and checks for errors.
        Returns a Document with transcript as content.
        """
        transcript = audio_manager.transcribe_file(file_path)
        
        if not transcript:
            return []
            
        if transcript.startswith("Error"):
            raise ValueError(f"Audio transcription failed: {transcript}")
            
        # Create metadata
        metadata = {
            "source": file_path,
            "type": "audio_transcript"
        }
        
        return [Document(page_content=transcript, metadata=metadata)]

