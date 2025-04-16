import sqlite3
import json
import logging
import threading
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .base import Database

# Configure logging
logger = logging.getLogger(__name__)


class SQLiteDatabase(Database):
    """
    SQLite implementation of the Database interface.
    Thread-safe version with connection per thread.
    """
    
    def __init__(self, db_path: str = "./database.sqlite"):
        """
        Initialize the SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._local.conn = None
        self._local.cursor = None
    
    def _get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create a new connection for this thread
            self._local.conn = sqlite3.connect(str(self.db_path))
            self._local.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self._local.cursor = self._local.conn.cursor()
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.debug(f"Created new SQLite connection for thread {threading.get_ident()}")
        
        return self._local.conn, self._local.cursor
    
    def initialize(self) -> None:
        """Initialize the database connection and create necessary tables."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get a connection for this thread
            conn, cursor = self._get_connection()
            
            logger.info(f"Initialized SQLite database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create the necessary tables in the database."""
        conn, cursor = self._get_connection()
        
        # Trials table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nct_id TEXT UNIQUE,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE,
            user_id TEXT,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indices
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_trials_nct_id ON trials (nct_id)
        ''')
        
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)
        ''')
        
        conn.commit()
    
    def close(self) -> None:
        """Close the database connection for the current thread."""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            try:
                self._local.conn.close()
                self._local.conn = None
                self._local.cursor = None
                logger.debug(f"Closed SQLite connection for thread {threading.get_ident()}")
            except Exception as e:
                logger.error(f"Error closing SQLite connection: {e}")
    
    def store_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Store clinical trials in the database.
        
        Args:
            trials: List of trial dictionaries
        """
        if not trials:
            logger.warning("No trials to store")
            return
        
        try:
            conn, cursor = self._get_connection()
            
            # Prepare data for insertion
            values = []
            for trial in trials:
                nct_id = trial.get("nct_id", trial.get("system_id", ""))
                if not nct_id:
                    continue
                    
                values.append((nct_id, json.dumps(trial)))
            
            # Insert trials
            cursor.executemany(
                '''
                INSERT OR REPLACE INTO trials (nct_id, data)
                VALUES (?, ?)
                ''',
                values
            )
            
            conn.commit()
            logger.info(f"Stored {len(values)} trials in the database")
        except Exception as e:
            logger.error(f"Error storing trials: {e}")
            if hasattr(self._local, 'conn') and self._local.conn is not None:
                self._local.conn.rollback()
            raise
    
    def get_trial(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a trial by NCT ID.
        
        Args:
            nct_id: NCT ID of the trial
            
        Returns:
            Trial dictionary or None if not found
        """
        try:
            conn, cursor = self._get_connection()
            
            # Query the database
            cursor.execute(
                '''
                SELECT data FROM trials WHERE nct_id = ?
                ''',
                (nct_id,)
            )
            
            result = cursor.fetchone()
            
            if result:
                return json.loads(result["data"])
            
            return None
        except Exception as e:
            logger.error(f"Error getting trial {nct_id}: {e}")
            raise
    
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
        try:
            conn, cursor = self._get_connection()
            
            # Build query
            query = "SELECT data FROM trials"
            
            # Add filters if provided
            if filters:
                # Since filters are applied to the JSON data, we need to fetch all results
                # and filter them in Python
                cursor.execute(f"{query} LIMIT ? OFFSET ?", (limit, offset))
                results = cursor.fetchall()
                
                # Parse and filter results
                parsed_results = []
                for result in results:
                    trial = json.loads(result["data"])
                    match = True
                    
                    for key, value in filters.items():
                        if key in trial and str(trial[key]).lower() != str(value).lower():
                            match = False
                            break
                    
                    if match:
                        parsed_results.append(trial)
                
                return parsed_results[:limit]
            else:
                # No filters, just paginate
                cursor.execute(f"{query} LIMIT ? OFFSET ?", (limit, offset))
                results = cursor.fetchall()
                
                # Parse results
                return [json.loads(result["data"]) for result in results]
        except Exception as e:
            logger.error(f"Error getting trials: {e}")
            raise
    
    def count_trials(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count trials with optional filtering.
        
        Args:
            filters: Optional dictionary of filters
            
        Returns:
            Number of trials
        """
        try:
            conn, cursor = self._get_connection()
            
            if filters:
                # Filters apply to JSON fields, so we need to count all and filter
                cursor.execute("SELECT COUNT(*) as count FROM trials")
                total = cursor.fetchone()["count"]
                
                # Count filtered trials
                cursor.execute("SELECT data FROM trials")
                results = cursor.fetchall()
                
                filtered_count = 0
                for result in results:
                    trial = json.loads(result["data"])
                    match = True
                    
                    for key, value in filters.items():
                        if key in trial and str(trial[key]).lower() != str(value).lower():
                            match = False
                            break
                    
                    if match:
                        filtered_count += 1
                
                return filtered_count
            else:
                # No filters, just count all
                cursor.execute("SELECT COUNT(*) as count FROM trials")
                return cursor.fetchone()["count"]
        except Exception as e:
            logger.error(f"Error counting trials: {e}")
            raise
    
    def store_conversation(self, 
                          conversation_id: str, 
                          messages: List[Dict[str, Any]],
                          user_id: str = "anonymous") -> None:
        """
        Store a conversation in the database.
        
        Args:
            conversation_id: ID of the conversation
            messages: List of message dictionaries
            user_id: ID of the user
        """
        try:
            conn, cursor = self._get_connection()
            
            # Check if conversation exists
            cursor.execute(
                '''
                SELECT conversation_id FROM conversations WHERE conversation_id = ?
                ''',
                (conversation_id,)
            )
            
            result = cursor.fetchone()
            
            if result:
                # Update existing conversation
                cursor.execute(
                    '''
                    UPDATE conversations 
                    SET messages = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE conversation_id = ?
                    ''',
                    (json.dumps(messages), conversation_id)
                )
            else:
                # Insert new conversation
                cursor.execute(
                    '''
                    INSERT INTO conversations (conversation_id, user_id, messages)
                    VALUES (?, ?, ?)
                    ''',
                    (conversation_id, user_id, json.dumps(messages))
                )
            
            conn.commit()
            logger.info(f"Stored conversation {conversation_id} with {len(messages)} messages")
        except Exception as e:
            logger.error(f"Error storing conversation {conversation_id}: {e}")
            if hasattr(self._local, 'conn') and self._local.conn is not None:
                self._local.conn.rollback()
            raise
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation dictionary or None if not found
        """
        try:
            conn, cursor = self._get_connection()
            
            # Query the database
            cursor.execute(
                '''
                SELECT conversation_id, user_id, messages, created_at, updated_at
                FROM conversations WHERE conversation_id = ?
                ''',
                (conversation_id,)
            )
            
            result = cursor.fetchone()
            
            if result:
                # Convert row to dictionary
                conversation = dict(result)
                conversation["messages"] = json.loads(conversation["messages"])
                return conversation
            
            return None
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            raise
    
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
        try:
            conn, cursor = self._get_connection()
            
            # Query the database
            cursor.execute(
                '''
                SELECT conversation_id, user_id, messages, created_at, updated_at
                FROM conversations 
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
                ''',
                (user_id, limit, offset)
            )
            
            results = cursor.fetchall()
            
            # Convert rows to dictionaries
            conversations = []
            for result in results:
                conversation = dict(result)
                conversation["messages"] = json.loads(conversation["messages"])
                conversations.append(conversation)
            
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            raise
