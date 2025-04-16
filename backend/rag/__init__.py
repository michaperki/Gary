import logging
from typing import List, Dict, Any, Optional

from core.vector_db.base import VectorDB
from core.llm.base import LLMProvider
from core.llm import LLMFactory
from .retriever import TrialRetriever
from .generator import ResponseGenerator

# Configure logging
logger = logging.getLogger(__name__)


class ClinicalTrialsRAG:
    """
    Retrieval-Augmented Generation system for clinical trials that connects
    the vector database with an LLM to answer user queries.
    """
    
    def __init__(self, 
                vector_db: VectorDB, 
                llm_provider: Optional[LLMProvider] = None,
                llm_provider_name: str = "openai",
                llm_model: Optional[str] = None):
        """
        Initialize the RAG system.
        
        Args:
            vector_db: Vector database instance
            llm_provider: Optional LLM provider instance
            llm_provider_name: Name of the LLM provider to use if provider not provided
            llm_model: Optional model name to use with the LLM provider
        """
        self.vector_db = vector_db
        
        # Set up LLM provider
        if llm_provider:
            self.llm_provider = llm_provider
        else:
            # Create LLM provider based on name
            kwargs = {}
            if llm_model:
                kwargs["model"] = llm_model
                
            self.llm_provider = LLMFactory.create(llm_provider_name, **kwargs)
            
            # Fall back to default provider if specified one is not available
            if not self.llm_provider:
                logger.warning(f"{llm_provider_name} provider not available, falling back to default")
                self.llm_provider = LLMFactory.create_default(**kwargs)
                
                if not self.llm_provider:
                    logger.error("No LLM provider available")
                    raise ValueError("No LLM provider available. Please provide API keys for OpenAI or Anthropic.")
        
        # Initialize components
        self.retriever = TrialRetriever(vector_db)
        self.generator = ResponseGenerator(self.llm_provider)
        
        logger.info(f"Initialized ClinicalTrialsRAG with {type(self.llm_provider).__name__}")
    
    def answer_question(self, 
                        query: str, 
                        n_results: int = 5, 
                        filters: Optional[Dict[str, Any]] = None,
                        conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a user question and generate an answer based on relevant clinical trials.
        
        Args:
            query: The user's question
            n_results: Number of results to retrieve from vector DB
            filters: Optional dictionary of explicit filters
            conversation_history: Optional conversation history
            
        Returns:
            Dict containing answer and supporting evidence
        """
        logger.info(f"Processing query: '{query}'")
        
        # Retrieve relevant trials
        retrieval_results = self.retriever.retrieve(
            query=query,
            n_results=n_results,
            explicit_filters=filters
        )
        
        # Generate response
        response = self.generator.generate_response(
            query=query,
            retrieval_results=retrieval_results,
            conversation_history=conversation_history
        )
        
        return response
