from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VectorDB(ABC):
    """
    Abstract base class for vector database implementations.
    
    This defines the interface that all vector database implementations must follow.
    """
    
    @abstractmethod
    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts to add
            metadatas: List of metadata dictionaries corresponding to each document
            ids: Optional list of IDs for the documents
        """
        pass
    
    @abstractmethod
    def query(self, query_text: str, n_results: int = 5, 
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query the vector database to find similar documents.
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            filters: Optional dictionary of metadata filters
            
        Returns:
            List of documents with similarity scores and metadata
        """
        pass
    
    @abstractmethod
    def get_filters_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options from the database.
        
        Returns:
            Dictionary of filter names to lists of possible values
        """
        pass
    
    @abstractmethod
    def load_trials_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Load clinical trial data from a JSON file.
        
        Args:
            json_file_path: Path to the JSON file
            
        Returns:
            List of trial dictionaries
        """
        pass
    
    @abstractmethod
    def load_trials_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Load clinical trial data from a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            List of trial dictionaries
        """
        pass
    
    @abstractmethod
    def process_and_index_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Process trial data into chunks and index in the vector database.
        
        Args:
            trials: List of clinical trial dictionaries
        """
        pass
    
    @abstractmethod
    def extract_unique_trials(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique trials from query results by NCT ID.
        
        Args:
            query_results: List of query result dictionaries
            
        Returns:
            List of unique trial dictionaries
        """
        pass
