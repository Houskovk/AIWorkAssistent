from duckduckgo_search import DDGS
import logging

class WebSearchTool:
    """Tool for performing web searches using DuckDuckGo."""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.ddgs = DDGS()

    def search(self, query: str) -> str:
        """
        Searches the web and returns a formatted string of results.
        params:
            query: The search query string.
        returns:
            String containing search results (Title, URL, Snippet).
        """
        try:
            results = self.ddgs.text(query, max_results=self.max_results)
            if not results:
                return "No web results found."
            
            formatted_results = []
            for i, res in enumerate(results, 1):
                title = res.get('title', 'No Title')
                href = res.get('href', '#')
                body = res.get('body', 'No description available.')
                formatted_results.append(f"Result {i}:\nTitle: {title}\nURL: {href}\nSnippet: {body}\n")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            logging.error(f"Web search failed: {e}")
            return f"Error performing web search: {str(e)}"

