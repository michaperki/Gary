import os
import logging
import importlib.util
from typing import Optional

from .base import VectorDB
from .minimal_vector_db import MinimalVectorDB

# Configure logging
logger = logging.getLogger(__name__)


class VectorDBFactory:
    """
    Factory class for creating vector database instances.
    """
    
    @staticmethod
    def create(db_type: str, **kwargs) -> Optional[VectorDB]:
        """
        Create a vector database instance.
        
        Args:
            db_type: Type of vector database to create
            **kwargs: Additional arguments to pass to the database constructor
            
        Returns:
            Vector database instance
        """
        db_type = db_type.lower()
        
        # Extract db_directory which is needed for MinimalVectorDB
        db_directory = kwargs.get('db_directory', './vector_db')
        
        # Minimal vector DB only accepts db_directory, filter other kwargs
        minimal_kwargs = {'db_directory': db_directory}
        
        if db_type == "minimal":
            logger.info("Creating MinimalVectorDB")
            return MinimalVectorDB(**minimal_kwargs)
        elif db_type == "transformer":
            # Check if transformer dependencies are available
            try:
                # Only import the module when requested
                if importlib.util.find_spec("sentence_transformers") is None:
                    raise ImportError("sentence_transformers module not found")
                
                # Check huggingface_hub compatibility
                import huggingface_hub
                hub_version = getattr(huggingface_hub, "__version__", "0.0.0")
                # Parse version and check if it's >= 0.23.0
                major, minor, patch = map(int, hub_version.split(".")[:3])
                if major == 0 and minor < 23:
                    logger.warning(f"huggingface_hub version {hub_version} is too old. Version 0.23.0 or later is required.")
                    logger.warning("Falling back to MinimalVectorDB")
                    return MinimalVectorDB(**minimal_kwargs)
                    
                # Import only when we're sure dependencies are compatible
                from .transformer_vector_db import TransformerVectorDB
                logger.info(f"Creating TransformerVectorDB with {kwargs}")
                return TransformerVectorDB(**kwargs)
            except ImportError as e:
                logger.warning(f"Cannot import necessary modules for TransformerVectorDB: {e}")
                logger.warning("Falling back to MinimalVectorDB")
                return MinimalVectorDB(**minimal_kwargs)
            except Exception as e:
                logger.error(f"Error creating TransformerVectorDB: {e}", exc_info=True)
                logger.warning("Falling back to MinimalVectorDB")
                return MinimalVectorDB(**minimal_kwargs)
        else:
            logger.error(f"Unknown vector database type: {db_type}")
            logger.warning("Falling back to MinimalVectorDB")
            return MinimalVectorDB(**minimal_kwargs)
    
    @staticmethod
    def create_default(db_directory: str = "./vector_db", **kwargs) -> VectorDB:
        """
        Create a default vector database instance based on available dependencies.
        
        Args:
            db_directory: Directory to store the database
            **kwargs: Additional arguments to pass to the database constructor
            
        Returns:
            Vector database instance
        """
        # First try to import sentence_transformers
        try:
            if importlib.util.find_spec("sentence_transformers") is None:
                raise ImportError("sentence_transformers module not found")
                
            # Check huggingface_hub compatibility
            import huggingface_hub
            hub_version = getattr(huggingface_hub, "__version__", "0.0.0")
            # Parse version and check if it's >= 0.23.0
            major, minor, patch = map(int, hub_version.split(".")[:3])
            if major == 0 and minor < 23:
                logger.warning(f"huggingface_hub version {hub_version} is too old. Version 0.23.0 or later is required.")
                logger.warning("Using MinimalVectorDB instead")
                return MinimalVectorDB(db_directory=db_directory)
                
            # Import only when we're sure dependencies are compatible
            from .transformer_vector_db import TransformerVectorDB
            logger.info("SentenceTransformers available, using TransformerVectorDB")
            return TransformerVectorDB(db_directory=db_directory, **kwargs)
        except ImportError as e:
            logger.info(f"SentenceTransformers not available: {e}")
            logger.info("Falling back to MinimalVectorDB")
            return MinimalVectorDB(db_directory=db_directory)
        except Exception as e:
            logger.error(f"Error initializing TransformerVectorDB: {e}", exc_info=True)
            logger.info("Falling back to MinimalVectorDB")
            return MinimalVectorDB(db_directory=db_directory)
