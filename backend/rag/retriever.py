import re
import logging
from typing import List, Dict, Any, Optional

from core.vector_db.base import VectorDB

# Configure logging
logger = logging.getLogger(__name__)


class TrialRetriever:
    """
    Responsible for retrieving clinical trials from the vector database
    based on user queries and filters.
    """
    
    def __init__(self, vector_db: VectorDB):
        """
        Initialize the retriever.
        
        Args:
            vector_db: Vector database to retrieve from
        """
        self.vector_db = vector_db
    
    def extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """
        Extract potential filters from a user query.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary of extracted filters
        """
        filters = {}
        
        # Extract phase information
        phase_match = re.search(r'phase (\d+)', query.lower())
        if phase_match:
            filters['phase'] = f"Phase {phase_match.group(1)}"
        
        # Extract gender filter (improved pattern matching)
        if re.search(r'\b(male|men|man)\b', query.lower()) and not re.search(r'\b(female|women|woman)\b', query.lower()):
            filters['gender'] = "Male"
        elif re.search(r'\b(female|women|woman)\b', query.lower()) and not re.search(r'\b(male|men|man)\b', query.lower()):
            filters['gender'] = "Female"
        
        # Extract healthy volunteer information
        if re.search(r'\bhealthy volunteers?\b', query.lower()):
            filters['healthy_volunteers'] = "yes"
        
        return filters
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance the query with additional terms to improve retrieval.
        
        Args:
            query: Original query string
            
        Returns:
            Enhanced query string
        """
        # This is a placeholder for query enhancement logic
        # In a real system, this could include:
        # - Synonym expansion
        # - Medical term normalization
        # - Query expansion with related terms
        return query
    
    def retrieve(self, 
                query: str, 
                n_results: int = 10, 
                explicit_filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant clinical trials based on the query.
        
        Args:
            query: User query string
            n_results: Number of results to retrieve
            explicit_filters: Optional dictionary of explicit filters
            
        Returns:
            List of retrieved trials
        """
        # Enhance the query
        enhanced_query = self.enhance_query(query)
        
        # Extract implicit filters from the query
        implicit_filters = self.extract_filters_from_query(query)
        
        # Combine implicit and explicit filters, with explicit taking precedence
        filters = implicit_filters
        if explicit_filters:
            filters.update(explicit_filters)
        
        logger.info(f"Retrieving trials with query: '{enhanced_query}', filters: {filters}")
        
        # Query the vector DB
        results = self.vector_db.query(
            query_text=enhanced_query,
            n_results=n_results * 2,  # Get more results initially for better coverage
            filters=filters
        )
        
        # Extract unique trials
        unique_trials = self.vector_db.extract_unique_trials(results)
        
        # Limit to requested number
        unique_trials = unique_trials[:n_results]
        
        logger.info(f"Retrieved {len(unique_trials)} unique trials")
        
        return unique_trials
