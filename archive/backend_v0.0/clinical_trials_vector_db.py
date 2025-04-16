# clinical_trials_vector_db.py
import json
import os
import pandas as pd
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import uuid
import re
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class CustomSentenceTransformerEmbedding:
    """Custom embedding function using sentence-transformers directly."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize with the model name."""
        self.model = SentenceTransformer(model_name)
    
    def __call__(self, texts):
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings

class ClinicalTrialsVectorDB:
    """
    Class to process clinical trial data and store in ChromaDB for vector search.
    """
    
    def __init__(self, db_directory: str = "./chroma_db"):
        """Initialize the vector database."""
        self.db_directory = db_directory
        os.makedirs(db_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_directory)
        
        # Use direct sentence-transformers for embeddings
        self.embedding_function = CustomSentenceTransformerEmbedding()
        
        # Create collection for clinical trials
        try:
            self.collection = self.client.get_collection(
                name="clinical_trials",
                embedding_function=self.embedding_function
            )
            print(f"Loaded existing collection with {self.collection.count()} documents")
        except ValueError:
            # Collection doesn't exist yet
            self.collection = self.client.create_collection(
                name="clinical_trials",
                embedding_function=self.embedding_function
            )
            print("Created new clinical trials collection")
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_trials_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Load clinical trial data from a JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            trials = json.load(f)
        
        print(f"Loaded {len(trials)} trials from {json_file_path}")
        return trials
    
    def load_trials_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Load clinical trial data from a CSV file."""
        df = pd.read_csv(csv_file_path)
        trials = df.to_dict(orient='records')
        
        print(f"Loaded {len(trials)} trials from {csv_file_path}")
        return trials
    
    def _create_trial_chunks(self, trial: Dict[str, Any]) -> List[Document]:
        """
        Split a single clinical trial into multiple chunks for better retrieval.
        Each chunk will maintain metadata about the original trial.
        """
        # Basic metadata that will be included with every chunk
        metadata = {
            "nct_id": trial.get("system_id", ""),
            "irb_number": trial.get("irb_number", ""),
            "title": trial.get("title", ""),
            "principal_investigator": trial.get("principal_investigator", ""),
            "phase": trial.get("phase", ""),
            "gender": trial.get("gender", ""),
            "age_range": trial.get("age", ""),
            "healthy_volunteers": "yes" if "accepting healthy volunteers" in 
                                 trial.get("healthy_volunteers", "").lower() else "no",
            "conditions": trial.get("conditions", ""),
            "interventions": trial.get("interventions", ""),
            "keywords": trial.get("keywords", ""),
            "source_url": f"https://clinicaltrials.gov/ct2/show/study/{trial.get('system_id', '')}"
        }
        
        # Create chunks for different sections of the trial
        chunks = []
        
        # Description chunk
        if trial.get("description"):
            description_text = f"DESCRIPTION: {trial.get('description')}"
            desc_chunks = self.text_splitter.create_documents(
                texts=[description_text],
                metadatas=[{**metadata, "chunk_type": "description"}]
            )
            chunks.extend(desc_chunks)
        
        # Eligibility criteria chunks
        if trial.get("inclusion_criteria") or trial.get("exclusion_criteria"):
            criteria_text = "ELIGIBILITY CRITERIA:\n"
            if trial.get("inclusion_criteria"):
                criteria_text += f"INCLUSION CRITERIA: {trial.get('inclusion_criteria')}\n\n"
            if trial.get("exclusion_criteria"):
                criteria_text += f"EXCLUSION CRITERIA: {trial.get('exclusion_criteria')}"
            
            criteria_chunks = self.text_splitter.create_documents(
                texts=[criteria_text],
                metadatas=[{**metadata, "chunk_type": "eligibility"}]
            )
            chunks.extend(criteria_chunks)
        
        # Overview chunk with basic trial information
        overview_text = f"""
        CLINICAL TRIAL OVERVIEW:
        Title: {trial.get('title', '')}
        NCT ID: {trial.get('system_id', '')}
        Phase: {trial.get('phase', '')}
        Principal Investigator: {trial.get('principal_investigator', '')}
        Conditions: {trial.get('conditions', '')}
        Interventions: {trial.get('interventions', '')}
        Gender eligibility: {trial.get('gender', '')}
        Age eligibility: {trial.get('age', '')}
        Accepts healthy volunteers: {"Yes" if "accepting healthy volunteers" in 
                                    trial.get('healthy_volunteers', '').lower() else "No"}
        """
        
        overview_chunks = self.text_splitter.create_documents(
            texts=[overview_text],
            metadatas=[{**metadata, "chunk_type": "overview"}]
        )
        chunks.extend(overview_chunks)
        
        return chunks
    
    def process_and_index_trials(self, trials: List[Dict[str, Any]]) -> None:
        """
        Process trial data into chunks and index in ChromaDB.
        """
        all_chunks = []
        ids = []
        documents = []
        metadatas = []
        
        # Process each trial into chunks
        for trial in trials:
            chunks = self._create_trial_chunks(trial)
            all_chunks.extend(chunks)
        
        # Prepare data for batch addition to ChromaDB
        for chunk in all_chunks:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            documents.append(chunk.page_content)
            metadatas.append(chunk.metadata)
        
        # Add to ChromaDB in batches (to avoid memory issues with large datasets)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            self.collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end]
            )
        
        print(f"Indexed {len(ids)} chunks from {len(trials)} clinical trials.")
    
    def query_trials(self, query: str, n_results: int = 5, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query the vector database to find relevant clinical trials.
        
        Args:
            query: User query string
            n_results: Number of results to return
            filters: Optional dictionary of metadata filters
            
        Returns:
            List of relevant clinical trial chunks
        """
        # Prepare the filter if provided
        where_filter = {}
        if filters:
            for key, value in filters.items():
                if value:  # Only add non-empty filters
                    where_filter[key] = {"$eq": value}
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def extract_unique_trials(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique trials from query results by NCT ID.
        """
        unique_trials = {}
        for result in query_results:
            nct_id = result['metadata']['nct_id']
            if nct_id not in unique_trials:
                unique_trials[nct_id] = result
            elif result['distance'] < unique_trials[nct_id]['distance']:
                # Keep the result with the smallest distance (most relevant)
                unique_trials[nct_id] = result
        
        return list(unique_trials.values())
    
    def get_filters_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options from the database.
        """
        # Query for unique values for various filter fields
        filters = {}
        
        try:
            # Get unique phases
            where = {"chunk_type": {"$eq": "overview"}}
            results = self.collection.get(
                where=where,
                include=["metadatas"]
            )
            
            if results and 'metadatas' in results and results['metadatas']:
                unique_phases = list(set([meta['phase'] for meta in results['metadatas'] if meta['phase']]))
                filters['phases'] = sorted(unique_phases)
            else:
                filters['phases'] = []
        except Exception as e:
            print(f"Error getting filter options: {e}")
            filters['phases'] = []
        
        return filters
