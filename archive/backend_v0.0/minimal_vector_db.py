# minimal_vector_db.py - Ultra-minimal implementation with no complex dependencies
import json
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from typing import List, Dict, Any, Optional
import uuid
import re

class MinimalVectorDB:
    """
    A minimal vector database implementation using scikit-learn's TF-IDF vectorizer
    that has minimal dependencies.
    """
    
    def __init__(self, db_directory: str = "./vector_db"):
        """Initialize the vector database."""
        self.db_directory = db_directory
        os.makedirs(db_directory, exist_ok=True)
        
        # Initialize the TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer()
        
        # Initialize empty database
        self.documents = []
        self.document_ids = []
        self.metadatas = []
        self.embeddings = None
        
        # Try to load existing database
        self._load_database()
        
        # Print database info for debugging
        if self.documents:
            print(f"Loaded vector database with {len(self.documents)} documents")
        else:
            print("No existing vector database found or failed to load")
    
    def _load_database(self):
        """Load existing database if available."""
        documents_path = os.path.join(self.db_directory, "documents.pkl")
        embeddings_path = os.path.join(self.db_directory, "embeddings.pkl")
        metadata_path = os.path.join(self.db_directory, "metadata.pkl")
        ids_path = os.path.join(self.db_directory, "ids.pkl")
        vectorizer_path = os.path.join(self.db_directory, "vectorizer.pkl")
        
        if all(os.path.exists(p) for p in [documents_path, embeddings_path, metadata_path, ids_path, vectorizer_path]):
            try:
                with open(documents_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                with open(ids_path, 'rb') as f:
                    self.document_ids = pickle.load(f)
                
                with open(metadata_path, 'rb') as f:
                    self.metadatas = pickle.load(f)
                
                with open(embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                print(f"Loaded database with {len(self.documents)} documents")
            except Exception as e:
                print(f"Error loading database: {e}")
                # Initialize empty database if loading fails
                self.documents = []
                self.document_ids = []
                self.metadatas = []
                self.embeddings = None
                self.vectorizer = TfidfVectorizer()
    
    def _save_database(self):
        """Save the current database."""
        documents_path = os.path.join(self.db_directory, "documents.pkl")
        embeddings_path = os.path.join(self.db_directory, "embeddings.pkl")
        metadata_path = os.path.join(self.db_directory, "metadata.pkl")
        ids_path = os.path.join(self.db_directory, "ids.pkl")
        vectorizer_path = os.path.join(self.db_directory, "vectorizer.pkl")
        
        try:
            with open(documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(ids_path, 'wb') as f:
                pickle.dump(self.document_ids, f)
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadatas, f)
            
            with open(embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
                
            print(f"Successfully saved database with {len(self.documents)} documents")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def load_trials_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Load clinical trial data from a JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            trials = json.load(f)
        
        return trials
    
    def load_trials_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Load clinical trial data from a CSV file."""
        df = pd.read_csv(csv_file_path)
        trials = df.to_dict(orient='records')
        
        return trials
    
    def _create_trial_chunks(self, trial: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split a single clinical trial into multiple chunks for better retrieval.
        Each chunk will maintain metadata about the original trial.
        """
        chunks = []
        
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
        
        # Create overview chunk
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
    
    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """Add documents to the vector database."""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
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
    
    def process_and_index_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Process trial data into chunks and index in the vector database.
        """
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
        
        print(f"Indexed {len(documents)} chunks from {len(trials)} clinical trials.")
    
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
            print("Warning: Vector database is empty. No results to return.")
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
            if filters:
                filtered_indices = []
                for i, metadata in enumerate(self.metadatas):
                    match = True
                    for key, value in filters.items():
                        if key in metadata and metadata[key] != value:
                            match = False
                            break
                    if match:
                        filtered_indices.append(i)
                
                if not filtered_indices:
                    return []
                
                # Sort filtered indices by similarity score
                filtered_indices = sorted(filtered_indices, key=lambda i: similarity_scores[i], reverse=True)
                top_indices = filtered_indices[:n_results]
            else:
                # Get indices of top n results
                top_indices = similarity_scores.argsort()[-n_results:][::-1]
            
            # Format results
            results = []
            for i in top_indices:
                results.append({
                    "id": self.document_ids[i],
                    "text": self.documents[i],
                    "metadata": self.metadatas[i],
                    "distance": 1.0 - similarity_scores[i]  # Convert similarity to distance
                })
            
            return results
        except Exception as e:
            print(f"Error during query: {e}")
            return []
    
    def extract_unique_trials(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique trials from query results by NCT ID.
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
        
        return list(unique_trials.values())
    
    def get_filters_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options from the database.
        """
        filters = {}
        
        # Get unique phases
        if self.metadatas:
            unique_phases = list(set([meta.get('phase', '') for meta in self.metadatas if meta.get('phase', '')]))
            filters['phases'] = sorted(unique_phases)
        else:
            filters['phases'] = []
        
        return filters
