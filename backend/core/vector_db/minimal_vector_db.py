import json
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import List, Dict, Any, Optional, Union
import uuid
import logging
from pathlib import Path

from .base import VectorDB

# Configure logging
logger = logging.getLogger(__name__)


class MinimalVectorDB(VectorDB):
    """
    An improved minimal vector database implementation using scikit-learn's TF-IDF vectorizer
    with enhanced performance and error handling.
    """
    
    def __init__(self, db_directory: str = "./vector_db"):
        """
        Initialize the vector database.
        
        Args:
            db_directory: Directory to store the database files
        """
        self.db_directory = Path(db_directory)
        self.db_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.documents: List[str] = []
        self.document_ids: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.embeddings: Optional[Union[np.ndarray, Any]] = None
        self.vectorizer = TfidfVectorizer(
            min_df=2, max_df=0.95,  # Improved defaults
            ngram_range=(1, 2),     # Include bigrams
            stop_words='english'    # Remove English stop words
        )
        
        # Load existing database
        self._load_database()
    
    def _get_file_paths(self) -> Dict[str, Path]:
        """
        Get paths to all database files.
        
        Returns:
            Dictionary of file names to paths
        """
        return {
            "documents": self.db_directory / "documents.pkl",
            "embeddings": self.db_directory / "embeddings.pkl",
            "metadata": self.db_directory / "metadata.pkl",
            "ids": self.db_directory / "ids.pkl",
            "vectorizer": self.db_directory / "vectorizer.pkl",
        }
    
    def _load_database(self) -> None:
        """Load existing database if available."""
        file_paths = self._get_file_paths()
        
        if all(path.exists() for path in file_paths.values()):
            try:
                with open(file_paths["documents"], 'rb') as f:
                    self.documents = pickle.load(f)
                
                with open(file_paths["ids"], 'rb') as f:
                    self.document_ids = pickle.load(f)
                
                with open(file_paths["metadata"], 'rb') as f:
                    self.metadatas = pickle.load(f)
                
                with open(file_paths["embeddings"], 'rb') as f:
                    self.embeddings = pickle.load(f)
                
                with open(file_paths["vectorizer"], 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                logger.info(f"Loaded database with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading database: {e}")
                # Initialize empty database if loading fails
                self.documents = []
                self.document_ids = []
                self.metadatas = []
                self.embeddings = None
                self.vectorizer = TfidfVectorizer(
                    min_df=2, max_df=0.95,
                    ngram_range=(1, 2),
                    stop_words='english'
                )
    
    def _save_database(self) -> None:
        """Save the current database."""
        file_paths = self._get_file_paths()
        
        try:
            with open(file_paths["documents"], 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(file_paths["ids"], 'wb') as f:
                pickle.dump(self.document_ids, f)
            
            with open(file_paths["metadata"], 'wb') as f:
                pickle.dump(self.metadatas, f)
            
            with open(file_paths["embeddings"], 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            with open(file_paths["vectorizer"], 'wb') as f:
                pickle.dump(self.vectorizer, f)
                
            logger.info(f"Successfully saved database with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise RuntimeError(f"Failed to save database: {e}")
    
    def load_trials_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Load clinical trial data from a JSON file.
        
        Args:
            json_file_path: Path to the JSON file
            
        Returns:
            List of trial dictionaries
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                trials = json.load(f)
            
            logger.info(f"Loaded {len(trials)} trials from {json_file_path}")
            return trials
        except Exception as e:
            logger.error(f"Error loading trials from {json_file_path}: {e}")
            raise
    
    def load_trials_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Load clinical trial data from a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            List of trial dictionaries
        """
        try:
            df = pd.read_csv(csv_file_path)
            trials = df.to_dict(orient='records')
            
            logger.info(f"Loaded {len(trials)} trials from {csv_file_path}")
            return trials
        except Exception as e:
            logger.error(f"Error loading trials from {csv_file_path}: {e}")
            raise
    
    def _create_trial_chunks(self, trial: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a single clinical trial into multiple chunks for better retrieval.
        Each chunk will maintain metadata about the original trial.
        
        Args:
            trial: Dictionary containing trial data
            
        Returns:
            List of dictionaries containing text chunks and metadata
        """
        chunks = []
        
        # Normalize missing values
        trial = {k: v if v is not None else "" for k, v in trial.items()}
        
        # Basic metadata that will be included with every chunk
        metadata = {
            "nct_id": trial.get("nct_id", trial.get("system_id", "")),
            "irb_number": trial.get("irb_number", ""),
            "title": trial.get("title", ""),
            "principal_investigator": trial.get("principal_investigator", ""),
            "phase": trial.get("phase", ""),
            "gender": trial.get("gender", ""),
            "age_range": trial.get("age_range", trial.get("age", "")),
            "healthy_volunteers": "yes" if "accepting healthy volunteers" in 
                                 trial.get("healthy_volunteers", "").lower() else "no",
            "conditions": trial.get("conditions", ""),
            "interventions": trial.get("interventions", ""),
            "keywords": trial.get("keywords", ""),
            "source_url": f"https://clinicaltrials.gov/ct2/show/study/{trial.get('nct_id', trial.get('system_id', ''))}"
        }
        
        # Create description chunk
        if trial.get("description"):
            chunks.append({
                "text": f"DESCRIPTION: {trial.get('description')}",
                "metadata": {**metadata, "chunk_type": "description"}
            })
        
        # Create eligibility criteria chunk
        if trial.get("inclusion_criteria") or trial.get("exclusion_criteria"):
            criteria_text = "ELIGIBILITY CRITERIA:\n"
            if trial.get("inclusion_criteria"):
                criteria_text += f"INCLUSION CRITERIA: {trial.get('inclusion_criteria')}\n\n"
            if trial.get("exclusion_criteria"):
                criteria_text += f"EXCLUSION CRITERIA: {trial.get('exclusion_criteria')}"
            
            chunks.append({
                "text": criteria_text,
                "metadata": {**metadata, "chunk_type": "eligibility"}
            })
        
        # Create overview chunk with improved formatting
        overview_text = f"""
        CLINICAL TRIAL OVERVIEW:
        Title: {trial.get('title', '')}
        NCT ID: {trial.get('nct_id', trial.get('system_id', ''))}
        Phase: {trial.get('phase', '')}
        Principal Investigator: {trial.get('principal_investigator', '')}
        Conditions: {trial.get('conditions', '')}
        Interventions: {trial.get('interventions', '')}
        Gender eligibility: {trial.get('gender', '')}
        Age eligibility: {trial.get('age_range', trial.get('age', ''))}
        Accepts healthy volunteers: {"Yes" if "accepting healthy volunteers" in 
                                    trial.get('healthy_volunteers', '').lower() else "No"}
        """
        
        chunks.append({
            "text": overview_text,
            "metadata": {**metadata, "chunk_type": "overview"}
        })
        
        return chunks
    
    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts to add
            metadatas: List of metadata dictionaries corresponding to each document
            ids: Optional list of IDs for the documents
        """
        if not documents:
            logger.warning("No documents to add")
            return
            
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # Ensure all lists have the same length
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("Documents, metadatas, and ids must have the same length")
        
        try:
            # If this is the first batch, fit the vectorizer
            if not self.documents:
                self.embeddings = self.vectorizer.fit_transform(documents)
            else:
                # Otherwise, transform with the existing vectorizer
                new_embeddings = self.vectorizer.transform(documents)
                if self.embeddings is not None:
                    if isinstance(self.embeddings, np.ndarray):
                        self.embeddings = np.vstack([self.embeddings, new_embeddings.toarray()])
                    else:
                        self.embeddings = np.vstack([self.embeddings.toarray(), new_embeddings.toarray()])
                else:
                    self.embeddings = new_embeddings
            
            # Add to database
            self.documents.extend(documents)
            self.document_ids.extend(ids)
            self.metadatas.extend(metadatas)
            
            # Save database
            self._save_database()
            
            logger.info(f"Added {len(documents)} documents to database")
        except Exception as e:
            logger.error(f"Error adding documents to database: {e}")
            raise
    
    def process_and_index_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Process trial data into chunks and index in the vector database.
        
        Args:
            trials: List of clinical trial dictionaries
        """
        if not trials:
            logger.warning("No trials to process")
            return
            
        all_chunks = []
        
        # Process each trial into chunks
        for trial in trials:
            chunks = self._create_trial_chunks(trial)
            all_chunks.extend(chunks)
        
        # Prepare data for addition to vector DB
        documents = [chunk["text"] for chunk in all_chunks]
        metadatas = [chunk["metadata"] for chunk in all_chunks]
        ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # Add to vector DB
        self.add(documents, metadatas, ids)
        
        logger.info(f"Indexed {len(documents)} chunks from {len(trials)} clinical trials")
    
    def query(self, query_text: str, n_results: int = 5, 
             filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query the vector database to find similar documents.
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            filters: Optional dictionary of metadata filters
            
        Returns:
            List of documents with similarity scores
        """
        if len(self.documents) == 0:
            logger.warning("Vector database is empty. No results to return.")
            return []
        
        # Validate inputs
        if not query_text:
            logger.warning("Empty query text")
            return []
            
        if n_results <= 0:
            logger.warning("Invalid n_results, must be > 0")
            return []
        
        try:
            # Transform query to TF-IDF vector space
            query_vector = self.vectorizer.transform([query_text])
            
            # Calculate similarity scores
            if isinstance(self.embeddings, np.ndarray):
                similarity_scores = cosine_similarity(query_vector, self.embeddings)[0]
            else:
                # If embeddings is a sparse matrix
                similarity_scores = cosine_similarity(query_vector, self.embeddings.toarray())[0]
            
            # Get indices of top results (handling filters)
            if filters and any(filters.values()):
                filtered_indices = []
                for i, metadata in enumerate(self.metadatas):
                    match = True
                    for key, value in filters.items():
                        # Skip empty filter values
                        if not value:
                            continue
                            
                        # Check if the metadata contains the key and the value matches
                        if key in metadata and metadata[key] != value:
                            match = False
                            break
                    if match:
                        filtered_indices.append(i)
                
                if not filtered_indices:
                    logger.info(f"No documents match the filters: {filters}")
                    return []
                
                # Sort filtered indices by similarity score
                filtered_indices = sorted(filtered_indices, key=lambda i: similarity_scores[i], reverse=True)
                top_indices = filtered_indices[:min(n_results, len(filtered_indices))]
            else:
                # Get indices of top n results
                top_indices = similarity_scores.argsort()[-min(n_results, len(similarity_scores)):][::-1]
            
            # Format results
            results = []
            for i in top_indices:
                results.append({
                    "id": self.document_ids[i],
                    "text": self.documents[i],
                    "metadata": self.metadatas[i],
                    "distance": 1.0 - similarity_scores[i]  # Convert similarity to distance
                })
            
            logger.info(f"Query returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise
    
    def extract_unique_trials(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique trials from query results by NCT ID.
        
        Args:
            query_results: List of query result dictionaries
            
        Returns:
            List of unique trial dictionaries
        """
        if not query_results:
            return []
            
        unique_trials = {}
        for result in query_results:
            if 'metadata' not in result:
                continue
                
            nct_id = result['metadata'].get('nct_id', '')
            if not nct_id:
                continue
                
            if nct_id not in unique_trials:
                unique_trials[nct_id] = result
            elif result.get('distance', 1.0) < unique_trials[nct_id].get('distance', 1.0):
                # Keep the result with the smallest distance (most relevant)
                unique_trials[nct_id] = result
        
        # Sort by distance (most relevant first)
        sorted_trials = sorted(
            unique_trials.values(), 
            key=lambda x: x.get('distance', 1.0)
        )
        
        return sorted_trials
    
    def get_filters_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options from the database.
        
        Returns:
            Dictionary of filter names to lists of possible values
        """
        filters = {}
        
        if not self.metadatas:
            return {
                'phases': [],
                'genders': [],
                'healthy_volunteers': []
            }
        
        # Extract unique values for each filter type
        phases = list(set([meta.get('phase', '') for meta in self.metadatas if meta.get('phase', '')]))
        genders = list(set([meta.get('gender', '') for meta in self.metadatas if meta.get('gender', '')]))
        healthy_volunteers = list(set([meta.get('healthy_volunteers', '') for meta in self.metadatas if meta.get('healthy_volunteers', '')]))
        
        filters['phases'] = sorted(phases)
        filters['genders'] = sorted(genders)
        filters['healthy_volunteers'] = sorted(healthy_volunteers)
        
        return filters
