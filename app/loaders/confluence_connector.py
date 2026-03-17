from typing import List, Optional
from langchain_community.document_loaders import ConfluenceLoader as LangChainConfluenceLoader
from langchain_core.documents import Document

class ConfluenceConnector:
    """Connector for fetching documents from Confluence."""
    
    def __init__(self, url: str, username: str, api_key: str):
        self.url = url
        self.username = username
        self.api_key = api_key

    def load(self, space_key: Optional[str] = None, page_id: Optional[str] = None, limit: int = 50) -> List[Document]:
        """
        Loads documents from Confluence.
        
        Args:
            space_key (str, optional): Key of the Space to load.
            page_id (str, optional): ID of a specific page to load.
            limit (int): Max number of pages to retrieve.
            
        Returns:
            List[Document]: List of LangChain documents.
        """
        loader = LangChainConfluenceLoader(
            url=self.url,
            username=self.username,
            api_key=self.api_key
        )
        
        documents = []
        try:
            if page_id:
                # Load specific page
                print(f"Loading Confluence page: {page_id}")
                documents = loader.load(page_ids=[page_id])
            elif space_key:
                # Load space with limit
                print(f"Loading Confluence space: {space_key} (limit={limit})")
                documents = loader.load(space_key=space_key, limit=limit)
            else:
                raise ValueError("Either space_key or page_id must be provided.")
                
            return documents
            
        except Exception as e:
            print(f"Error loading from Confluence: {e}")
            raise e


