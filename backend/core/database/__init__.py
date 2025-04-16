import os
import logging
from typing import Optional

from .base import Database
from .sqlite_db import SQLiteDatabase

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseFactory:
    """
    Factory class for creating database instances.
    """
    
    @staticmethod
    def create(db_type: str, **kwargs) -> Optional[Database]:
        """
        Create a database instance.
        
        Args:
            db_type: Type of database to create
            **kwargs: Additional arguments to pass to the database constructor
            
        Returns:
            Database instance
        """
        db_type = db_type.lower()
        
        if db_type == "sqlite":
            db = SQLiteDatabase(**kwargs)
            db.initialize()
            return db
        else:
            logger.error(f"Unknown database type: {db_type}")
            return None
    
    @staticmethod
    def create_default(db_path: str = "./database.sqlite", **kwargs) -> Database:
        """
        Create a default database instance.
        
        Args:
            db_path: Path to the database
            **kwargs: Additional arguments to pass to the database constructor
            
        Returns:
            Database instance
        """
        db = SQLiteDatabase(db_path=db_path, **kwargs)
        db.initialize()
        return db
