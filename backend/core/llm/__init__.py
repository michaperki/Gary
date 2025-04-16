import os
import logging
from typing import Optional, Dict, Any

from .base import LLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider

# Configure logging
logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory class for creating LLM provider instances.
    """
    
    @staticmethod
    def create(provider_name: str, **kwargs) -> Optional[LLMProvider]:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider to create
            **kwargs: Additional arguments to pass to the provider constructor
            
        Returns:
            LLM provider instance or None if the provider is not available
        """
        provider_name = provider_name.lower()
        
        if provider_name == "openai":
            provider = OpenAIProvider(**kwargs)
        elif provider_name == "anthropic":
            provider = AnthropicProvider(**kwargs)
        else:
            logger.error(f"Unknown provider: {provider_name}")
            return None
        
        # Check if the provider is available
        if not provider.is_available():
            logger.warning(f"{provider_name} provider is not available")
            return None
        
        return provider
    
    @staticmethod
    def create_default(**kwargs) -> Optional[LLMProvider]:
        """
        Create a default LLM provider instance based on available API keys.
        
        Args:
            **kwargs: Additional arguments to pass to the provider constructor
            
        Returns:
            LLM provider instance or None if no provider is available
        """
        # Try OpenAI first
        if os.environ.get("OPENAI_API_KEY"):
            provider = OpenAIProvider(**kwargs)
            if provider.is_available():
                logger.info("Using OpenAI as default LLM provider")
                return provider
        
        # Try Anthropic next
        if os.environ.get("ANTHROPIC_API_KEY"):
            provider = AnthropicProvider(**kwargs)
            if provider.is_available():
                logger.info("Using Anthropic as default LLM provider")
                return provider
        
        logger.error("No LLM provider available")
        return None
