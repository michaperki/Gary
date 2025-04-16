import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Configuration class for the application.
    """
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """
        Get the application configuration.
        
        Returns:
            Dictionary containing configuration values
        """
        config = {
            # API configuration
            "PORT": int(os.environ.get("PORT", 5000)),
            "DEBUG": os.environ.get("DEBUG", "True").lower() in ("true", "1", "t"),
            
            # Database configuration
            "VECTOR_DB_PATH": os.environ.get("VECTOR_DB_PATH", "./vector_db"),
            
            # LLM configuration
            "LLM_PROVIDER": os.environ.get("LLM_PROVIDER", "openai"),
            "LLM_MODEL": os.environ.get("LLM_MODEL"),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
            
            # Application configuration
            "MAX_RESULTS": int(os.environ.get("MAX_RESULTS", 10)),
            "RESPONSE_LENGTH": int(os.environ.get("RESPONSE_LENGTH", 800)),
        }
        
        return config
    
    @staticmethod
    def validate_config() -> Optional[str]:
        """
        Validate the application configuration.
        
        Returns:
            Error message if configuration is invalid, None otherwise
        """
        config = Config.get_config()
        
        # Check for required configuration
        if not config.get("VECTOR_DB_PATH"):
            return "VECTOR_DB_PATH is required"
        
        # Check for LLM configuration
        if not (config.get("OPENAI_API_KEY") or config.get("ANTHROPIC_API_KEY")):
            return "Either OPENAI_API_KEY or ANTHROPIC_API_KEY is required for chat functionality"
        
        return None
