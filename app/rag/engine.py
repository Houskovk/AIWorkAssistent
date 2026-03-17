from typing import List, Generator, Dict, Any
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import settings
from app.core.interfaces import IDocumentLoader, IVectorStore, ILLMClient
from app.loaders.loader_factory import DocumentLoaderFactory
from app.vectorstore.chroma_store import ChromaStore
from app.llm.ollama_client import OllamaClient
from app.loaders.confluence_connector import ConfluenceConnector
from app.rag.prompts import GRADER_PROMPT, ROUTER_PROMPT, COMPARISON_PROMPT
from app.tools.web_search import WebSearchTool
from app.rag.evaluator import Evaluator

class RAGEngine:
    """Core RAG logic orchestrator."""
    
    def __init__(self):
        self.vector_store: IVectorStore = ChromaStore()
        self.llm_client: ILLMClient = OllamaClient()
        self.evaluator = Evaluator(self.llm_client)
        self.web_search_tool = WebSearchTool()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            add_start_index=True,
        )
        self.last_interaction: Dict[str, str] = {}

    def ingest_file(self, file_path: str) -> None:
        """Loads a file, splits it, and stores embeddings."""
        print(f"Ingesting file: {file_path}")
        try:
            loader: IDocumentLoader = DocumentLoaderFactory.get_loader(file_path)
            documents = loader.load(file_path)
            
            if not documents:
                print(f"No content extracted from {file_path}")
                return

            chunks = self.text_splitter.split_documents(documents)
            print(f"Split into {len(chunks)} chunks.")
            
            self.vector_store.add_documents(chunks)
            print(f"Added {len(chunks)} chunks to vector store.")
            
        except Exception as e:
            print(f"Error ingesting file {file_path}: {e}")
            raise e

    def ingest_confluence(self, url: str, username: str, api_key: str, space_key: str = None, page_id: str = None, limit: int = 50) -> None:
        """Ingests documents from Confluence."""
        print(f"Ingesting from Confluence: {url}")
        try:
            connector = ConfluenceConnector(url, username, api_key)
            documents = connector.load(space_key=space_key, page_id=page_id, limit=limit)
            
            if not documents:
                print("No documents found in Confluence.")
                return

            chunks = self.text_splitter.split_documents(documents)
            print(f"Split Confluence content into {len(chunks)} chunks.")
            
            self.vector_store.add_documents(chunks)
            print(f"Added {len(chunks)} chunks to vector store.")
            
        except Exception as e:
            print(f"Error ingesting from Confluence: {e}")
            raise e

    def _evaluate_answer(self, question: str, context: str, answer: str) -> bool:
        """Evaluates model response for accuracy and hallucination."""
        # Clean answer to remove potential preambles if needed, but simple string is fine
        prompt = GRADER_PROMPT.format(question=question, context=context, answer=answer)
        evaluation = self.llm_client.generate_text(prompt)
        print(f"Reflection Score: {evaluation}")
        # Relaxed checking: if explicit YES or just starts with YES
        return "YES" in evaluation or "Score: YES" in evaluation or "SCORE: YES" in evaluation

    def _should_search_web(self, query: str) -> bool:
        """Decides if the query requires external web search."""
        prompt = ROUTER_PROMPT.format(question=query)
        decision = self.llm_client.generate_text(prompt)
        decision = decision.upper().strip()
        print(f"Router Decision: {decision}")
        return "YES" in decision

    def ask(self, query: str, history: List[Dict[str, str]] = None, use_web_search: bool = True) -> Generator[str, None, None]:
        """Queries the knowledge base and generates a response with self-correction."""
        
        start_time = time.time()

        # 0. Router Check
        is_web_search = use_web_search and self._should_search_web(query)
        
        # 1. Retrieve relevant local documents
        relevant_docs = self.vector_store.search(query, k=settings.RETRIEVAL_K)
        
        # Extract source files
        source_files = list(set([doc.metadata.get("source", "Unknown") for doc in relevant_docs]))

        local_context_str = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        final_context_str = ""
        prompt_to_use = ""

        # 2. Logic Branch (Web vs Local)
        if is_web_search:
            yield "🔎 Detecting need for verification. Searching the web for external comparison...\n\n"
            web_context_str = self.web_search_tool.search(query)
            
            # Combine contexts
            final_context_str = f"=== LOCAL CONTEXT ===\n{local_context_str}\n\n=== WEB CONTEXT ===\n{web_context_str}"
            
            # Use comparison prompt
            prompt_to_use = COMPARISON_PROMPT.format(
                question=query, 
                local_context=local_context_str, 
                web_context=web_context_str
            )
        else:
            # Local only
            if not local_context_str:
                yield "No relevant local context found."
                return
            final_context_str = local_context_str
            prompt_to_use = f"Context: {final_context_str}\n\nQuestion: {query}\n\nAnswer:"

        # 3. Generation Loop
        current_try = 0
        best_answer = ""
        
        while current_try <= settings.MAX_RETRIES:
            if current_try > 0:
                yield f"\n*(Self-Correction attempt {current_try}/{settings.MAX_RETRIES})* \n"

            # Generate full answer
            full_answer_text = self.llm_client.generate_text(prompt_to_use)
            
            # Evaluate using GRADER_PROMPT against the COMBINED context
            # (If it used web, it must be supported by local+web)
            is_valid = self._evaluate_answer(query, final_context_str, full_answer_text)
            
            elapsed_time = time.time() - start_time

            # Store interaction for later metrics calculation
            self.last_interaction = {
                "question": query,
                "context": final_context_str,
                "answer": full_answer_text,
                "duration": elapsed_time,
                "source_files": source_files,
                "used_web_search": is_web_search
            }
            
            if is_valid:
                yield full_answer_text
                return
            else:
                print(f"Try {current_try} failed verification. Retrying...")
                current_try += 1
                best_answer = full_answer_text 
        
        # If all retries failed
        yield f"\n*(Warning: The model was unsure about this answer)*\n{best_answer}"
        
        elapsed_time = time.time() - start_time
        
        # Store even if failed
        self.last_interaction = {
            "question": query,
            "context": final_context_str,
            "answer": best_answer,
            "duration": elapsed_time,
            "source_files": source_files,
            "used_web_search": is_web_search
        }

    def compute_metrics(self) -> Dict[str, Any]:
        """Computes evaluation metrics for the last interaction."""
        if not self.last_interaction:
            return {"error": "No recent interaction to evaluate."}
            
        print("Computing metrics...")
        metrics = self.evaluator.evaluate(
            self.last_interaction["question"],
            self.last_interaction["context"],
            self.last_interaction["answer"]
        )
        
        # Add performance stats (flattened)
        metrics["duration"] = self.last_interaction.get("duration", 0.0)
        metrics["source_files"] = self.last_interaction.get("source_files", [])
        metrics["used_web_search"] = self.last_interaction.get("used_web_search", False)
        
        return metrics

    def clear_data(self) -> None:
        """Clears all data from the system."""
        self.vector_store.clear()
        
    def list_files(self) -> List[str]:
        """Listing files is tricky with Chroma alone as it doesn't store file list explicitly in a simple way.
        We can iterate over documents or maintain a separate metadata store.
        For simplicity, we might just look at the upload directory."""
        if not os.path.exists(settings.UPLOAD_DIR):
            return []
        return os.listdir(settings.UPLOAD_DIR)

    def ingest_directory(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Ingests all supported files in a directory recursively.
        Returns a dict with 'processed', 'skipped' (unsupported), and 'errors' lists.
        """
        results = {"processed": [], "skipped": [], "errors": []}
        
        if not os.path.isdir(directory_path):
             raise ValueError(f"Path is not a directory: {directory_path}")

        print(f"Scanning directory: {directory_path}")
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check for supported extension before trying to ingest?
                # Or just rely on ingest_file raising ValueError
                
                try:
                    self.ingest_file(file_path)
                    results["processed"].append(file_path)
                except ValueError as ve:
                    # Assuming ValueError from DocumentLoaderFactory means unsupported extension
                    # But ingest_file re-raises generic Exception if it wraps it?
                    # ingest_file: try... except Exception as e: raise e
                    # So if DocumentLoaderFactory raises ValueError, ingest_file raises ValueError.
                    if "No loader found" in str(ve):
                        results["skipped"].append(file_path)
                    else:
                        results["errors"].append(f"{file_path}: {ve}")
                except Exception as e:
                    results["errors"].append(f"{file_path}: {e}")
                    
        return results

