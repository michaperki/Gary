from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class Database(ABC):
    """
    Abstract base class for database implementations.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the database connection and create necessary tables."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    def store_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Store clinical trials in the database.
        
        Args:
            trials: List of trial dictionaries
        """
        pass
    
    @abstractmethod
    def get_trial(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a trial by NCT ID.
        
        Args:
            nct_id: NCT ID of the trial
            
        Returns:
            Trial dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def get_trials(self, 
                  filters: Optional[Dict[str, Any]] = None, 
                  limit: int = 100, 
                  offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get trials with optional filtering.
        
        Args:
            filters: Optional dictionary of filters
            limit: Maximum number of trials to return
            offset: Offset for pagination
            
        Returns:
            List of trial dictionaries
        """
        pass
    
    @abstractmethod
    def count_trials(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count trials with optional filtering.
        
        Args:
            filters: Optional dictionary of filters
            
        Returns:
            Number of trials
        """
        pass
    
    @abstractmethod
    def store_conversation(self, 
                          conversation_id: str, 
                          messages: List[Dict[str, Any]]) -> None:
        """
        Store a conversation in the database.
        
        Args:
            conversation_id: ID of the conversation
            messages: List of message dictionaries
        """
        pass
    
    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def get_user_conversations(self, 
                              user_id: str, 
                              limit: int = 10, 
                              offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get conversations for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversation dictionaries
        """
        pass
