from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class LLMProvider(ABC):
    """
    Abstract base class for LLM provider implementations.
    
    This defines the interface that all LLM provider implementations must follow.
    """
    
    @abstractmethod
    def generate_response(self, 
                         prompt: str, 
                         system_message: Optional[str] = None,
                         conversation_history: Optional[List[Dict[str, str]]] = None,
                         temperature: float = 0.7,
                         max_tokens: int = 1000) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            system_message: Optional system message for the LLM
            conversation_history: Optional list of conversation history messages
            temperature: Temperature parameter for response generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated response as a string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available and properly configured.
        
        Returns:
            True if the provider is available, False otherwise
        """
        pass
