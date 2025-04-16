#!/usr/bin/env python
"""
This script rebuilds the vector database from scratch.
Use this when you need to recreate the embeddings with a new model.
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path

from core.vector_db import VectorDBFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Rebuild the vector database")
    parser.add_argument(
        "--db-type",
        type=str,
        choices=["minimal", "transformer"],
        default="minimal",
        help="Type of vector database to create"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="./vector_db",
        help="Path to the vector database directory"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Name of the SentenceTransformer model to use (only for transformer type)"
    )
    parser.add_argument(
        "--trials-file",
        type=str,
        required=True,
        help="Path to the trials file (JSON or CSV)"
    )
    parser.add_argument(
        "--file-type",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Type of the trials file"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a backup of the existing vector database"
    )
    
    return parser.parse_args()

def backup_database(db_path: str) -> None:
    """
    Create a backup of the existing vector database.
    
    Args:
        db_path: Path to the vector database directory
    """
    db_path = Path(db_path)
    if not db_path.exists():
        logger.info(f"No existing database to backup at {db_path}")
        return
    
    # Create backup directory
    backup_dir = db_path.parent / f"{db_path.name}_backup_{int(os.times()[4])}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files to backup directory
    for file_path in db_path.glob("*"):
        if file_path.is_file():
            shutil.copy2(file_path, backup_dir / file_path.name)
    
    logger.info(f"Created backup at {backup_dir}")

def clean_database(db_path: str) -> None:
    """
    Remove existing vector database files.
    
    Args:
        db_path: Path to the vector database directory
    """
    db_path = Path(db_path)
    if not db_path.exists():
        logger.info(f"No existing database to clean at {db_path}")
        return
    
    # Remove existing files
    for file_path in db_path.glob("*"):
        if file_path.is_file():
            file_path.unlink()
    
    logger.info(f"Cleaned database at {db_path}")

def main():
    """Main function."""
    args = parse_args()
    
    try:
        # Validate trials file
        trials_path = Path(args.trials_file)
        if not trials_path.exists():
            logger.error(f"Trials file not found: {trials_path}")
            sys.exit(1)
        
        # Backup existing database if requested
        if args.backup:
            backup_database(args.db_path)
        
        # Clean existing database
        clean_database(args.db_path)
        
        # Create vector database
        logger.info(f"Creating {args.db_type} vector database at {args.db_path}")
        
        if args.db_type == "transformer":
            vector_db = VectorDBFactory.create(
                db_type=args.db_type,
                db_directory=args.db_path,
                model_name=args.model_name
            )
        else:
            vector_db = VectorDBFactory.create(
                db_type=args.db_type,
                db_directory=args.db_path
            )
        
        if vector_db is None:
            logger.error(f"Failed to create vector database of type {args.db_type}")
            sys.exit(1)
        
        # Load trials
        logger.info(f"Loading trials from {trials_path}")
        
        if args.file_type.lower() == "json":
            trials = vector_db.load_trials_from_json(str(trials_path))
        elif args.file_type.lower() == "csv":
            trials = vector_db.load_trials_from_csv(str(trials_path))
        else:
            logger.error(f"Unknown file type: {args.file_type}")
            sys.exit(1)
        
        logger.info(f"Loaded {len(trials)} trials")
        
        # Process and index trials
        logger.info("Processing and indexing trials...")
        vector_db.process_and_index_trials(trials)
        
        logger.info("Vector database rebuilt successfully!")
        
    except Exception as e:
        logger.error(f"Error rebuilding vector database: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
