import os
import logging
from typing import List, Dict, Any, Optional, Union
import requests

from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    Implementation of the LLMProvider interface for OpenAI's API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use (defaults to gpt-4)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
    
    def is_available(self) -> bool:
        """
        Check if the OpenAI API is available and properly configured.
        
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
        Generate a response from the OpenAI API.
        
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
            logger.error("OpenAI API key not provided")
            return "Error: OpenAI API key not provided."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            # Make the API request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Add timeout for better error handling
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                error_message = f"API request failed with status code {response.status_code}. {response.text}"
                logger.error(error_message)
                return f"Error: {error_message}"
                
        except requests.RequestException as e:
            error_message = f"Request to OpenAI API failed: {str(e)}"
            logger.error(error_message)
            return f"Error connecting to OpenAI API: {str(e)}"
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.error(error_message)
            return f"Unexpected error: {str(e)}"
