import os
import logging
from typing import List, Dict, Any, Optional, Union
import requests

from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Implementation of the LLMProvider interface for Anthropic's API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
            model: Model to use (defaults to claude-3-opus-20240229)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        
        if not self.api_key:
            logger.warning("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
    
    def is_available(self) -> bool:
        """
        Check if the Anthropic API is available and properly configured.
        
        Returns:
            True if the API is available, False otherwise
        """
        return bool(self.api_key)
    
    def generate_response(self, 
                         prompt: str, 
                         system_message: Optional[str] = None,
                         conversation_history: Optional[List[Dict[str, str]]] = None,
                         temperature: float = 0.7,
                         max_tokens: int = 1000) -> str:
        """
        Generate a response from the Anthropic API.
        
        Args:
            prompt: The prompt to send to the API
            system_message: Optional system message for the conversation
            conversation_history: Optional list of conversation history messages
            temperature: Temperature parameter for response generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated response as a string
        """
        if not self.is_available():
            logger.error("Anthropic API key not provided")
            return "Error: Anthropic API key not provided."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Prepare messages
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add system message if provided
        if system_message:
            data["system"] = system_message
        
        try:
            # Make the API request
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30  # Add timeout for better error handling
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                error_message = f"API request failed with status code {response.status_code}. {response.text}"
                logger.error(error_message)
                return f"Error: {error_message}"
                
        except requests.RequestException as e:
            error_message = f"Request to Anthropic API failed: {str(e)}"
            logger.error(error_message)
            return f"Error connecting to Anthropic API: {str(e)}"
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(error_message)
            return f"Unexpected error: {str(e)}"
