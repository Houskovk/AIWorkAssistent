import json
import re
from typing import Dict, Any
from app.core.interfaces import ILLMClient
from app.rag.prompts import METRICS_PROMPT

class Evaluator:
    """Evaluates the quality of RAG responses."""
    
    def __init__(self, llm_client: ILLMClient):
        self.llm_client = llm_client

    def evaluate(self, question: str, context: str, answer: str) -> Dict[str, Any]:
        """
        Computes relevance, faithfulness, and clarity metrics.
        Returns a dictionary with scores and reasoning.
        """
        prompt = METRICS_PROMPT.format(
            question=question,
            context=context,
            answer=answer
        )
        
        response = self.llm_client.generate_text(prompt)
        
        # Try to parse JSON from the response
        try:
            # Look for JSON block if wrapped in markdown
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                metrics = json.loads(json_str)
            else:
                # Fallback: try raw response
                metrics = json.loads(response)
                
            return {
                "relevance": metrics.get("relevance", 0),
                "faithfulness": metrics.get("faithfulness", 0),
                "clarity": metrics.get("clarity", 0),
                "reasoning": metrics.get("reasoning", "No reasoning provided.")
            }
        except Exception as e:
            print(f"Error parsing metrics: {e}")
            print(f"Raw LLM response: {response}")
            return {
                "relevance": 0,
                "faithfulness": 0,
                "clarity": 0,
                "reasoning": "Failed to parse evaluation metrics."
            }

