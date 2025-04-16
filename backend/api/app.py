import os
import logging
from flask import Flask
from flask_cors import CORS
from typing import Dict, Any, Optional

from core.vector_db import VectorDBFactory
from core.database import DatabaseFactory
from core.llm import LLMFactory
from rag import ClinicalTrialsRAG
from .routes.search_routes import create_search_routes
from .routes.chat_routes import create_chat_routes
from .routes.admin_routes import create_admin_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Set up CORS
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], 
                               "allow_headers": ["Content-Type", "Authorization"]}})
    
    # Load configuration
    if config:
        app.config.update(config)
    
    # Initialize components
    
    # Initialize vector database
    vector_db_type = os.environ.get("VECTOR_DB_TYPE", "default")
    vector_db_path = os.environ.get("VECTOR_DB_PATH", "./vector_db")
    
    # Create vector database based on configuration
    if vector_db_type.lower() == "default":
        vector_db = VectorDBFactory.create_default(db_directory=vector_db_path)
    else:
        vector_db = VectorDBFactory.create(
            db_type=vector_db_type,
            db_directory=vector_db_path,
            model_name=os.environ.get("VECTOR_DB_MODEL", "all-MiniLM-L6-v2")
        )
    
    # Initialize database
    db_type = os.environ.get("DB_TYPE", "sqlite")
    db_path = os.environ.get("DB_PATH", "./database.sqlite")
    
    # Create database based on configuration
    if db_type.lower() == "sqlite" or db_type.lower() == "default":
        database = DatabaseFactory.create_default(db_path=db_path)
    else:
        database = DatabaseFactory.create(
            db_type=db_type,
            db_path=db_path
        )
    
    # Set up LLM provider
    llm_provider_name = os.environ.get("LLM_PROVIDER", "openai")
    llm_model = os.environ.get("LLM_MODEL")
    
    # Create RAG system
    try:
        rag_system = ClinicalTrialsRAG(
            vector_db=vector_db,
            llm_provider_name=llm_provider_name,
            llm_model=llm_model
        )
        logger.info(f"Initialized RAG system with {llm_provider_name} provider")
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}", exc_info=True)
        rag_system = None
    
    # Register routes
    app.register_blueprint(create_search_routes(vector_db, database))
    app.register_blueprint(create_admin_routes(vector_db, database))
    
    # Only register chat routes if RAG system is available
    if rag_system:
        app.register_blueprint(create_chat_routes(rag_system, database))
    else:
        logger.warning("Chat functionality disabled due to unavailable LLM provider")
        
        @app.route('/api/chat', methods=['POST', 'OPTIONS'])
        def chat_disabled():
            return {
                "error": "Chat functionality is disabled. Please configure an LLM provider (OpenAI or Anthropic)."
            }, 503
    
    # Cleanup database connection on app teardown
    @app.teardown_appcontext
    def close_database(exception):
        try:
            if database:
                database.close()
        except Exception as e:
            logger.error(f"Error during database connection cleanup: {e}")
            # Don't re-raise the exception to avoid interfering with response handling
        
        def chat_disabled():
            return {
                "error": "Chat functionality is disabled. Please configure an LLM provider (OpenAI or Anthropic)."
            }, 503
    
    logger.info("Application initialized")
    return app


app = create_app()
