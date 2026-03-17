from typing import Generator, List, Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.config.settings import settings
from app.core.interfaces import ILLMClient

class OllamaClient(ILLMClient):
    """Implementation of ILLMClient using Ollama."""
    
    def __init__(self):
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0.7
        )

    def generate_response(self, prompt: str, context: Optional[str] = None, history: List[Dict[str, str]] = None) -> Generator[str, None, None]:
        """Generates a streaming response from Ollama."""
        
        messages = []
        
        # System prompt with context
        system_prompt = "You are a helpful AI assistant."
        if context:
            system_prompt += f"\n\nContext information is below:\n---------------------\n{context}\n---------------------\nAnswer the question using the context above. If the answer is not in the context, say so."
            
        messages.append(SystemMessage(content=system_prompt))
        
        # Chat history
        if history:
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # Current user message
        messages.append(HumanMessage(content=prompt))
        
        # Stream response
        for chunk in self.llm.stream(messages):
            yield chunk.content

    def generate_text(self, prompt: str) -> str:
        """Generates a non-streaming string response from the LLM."""
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content
