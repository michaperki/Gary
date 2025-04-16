import os
import json
from typing import List, Dict, Any, Optional
from simple_vector_db import SimpleVectorDB
import requests
import re

class ClinicalTrialsRAG:
    """
    Retrieval-Augmented Generation system for clinical trials that connects
    the vector database with an LLM to answer user queries.
    """
    
    def __init__(self, vector_db: SimpleVectorDB, 
                openai_api_key: Optional[str] = None,
                anthropic_api_key: Optional[str] = None):
        """
        Initialize the RAG system with a vector database and API keys.
        
        Args:
            vector_db: Instance of SimpleVectorDB
            openai_api_key: API key for OpenAI (optional)
            anthropic_api_key: API key for Anthropic (optional)
        """
        self.vector_db = vector_db
        
        # Set API keys from arguments or environment variables
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        # Check if at least one API key is available
        if not self.openai_api_key and not self.anthropic_api_key:
            print("Warning: No LLM API keys provided. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
    
    def _format_context_for_llm(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """
        Format the retrieved clinical trial information for the LLM prompt.
        
        Args:
            retrieval_results: Results from vector database query
            
        Returns:
            Formatted context string
        """
        context = "CLINICAL TRIAL INFORMATION:\n\n"
        
        for i, result in enumerate(retrieval_results):
            meta = result['metadata']
            context += f"[Trial {i+1}] {meta['title']}\n"
            context += f"NCT ID: {meta['nct_id']}\n"
            context += f"PI: {meta['principal_investigator']}\n"
            context += f"Phase: {meta['phase']}\n"
            context += f"Conditions: {meta['conditions']}\n"
            
            # Add the relevant chunk content
            content = result['text'].strip()
            context += f"Content: {content}\n\n"
        
        return context
    
    def query_openai(self, prompt: str) -> str:
        """
        Query the OpenAI API with a prompt.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The LLM's response
        """
        if not self.openai_api_key:
            return "Error: OpenAI API key not provided."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        data = {
            "model": "gpt-4",  # Using GPT-4 for better medical understanding
            "messages": [
                {"role": "system", "content": "You are a clinical research assistant helping doctors find relevant clinical trials for their patients. Provide accurate information based on clinical trial data and cite the appropriate NCT ID for your information."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3  # Lower temperature for more factual responses
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: API request failed with status code {response.status_code}. {response.text}"
                
        except Exception as e:
            return f"Error connecting to OpenAI API: {str(e)}"
    
    def query_anthropic(self, prompt: str) -> str:
        """
        Query the Anthropic API with a prompt.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The LLM's response
        """
        if not self.anthropic_api_key:
            return "Error: Anthropic API key not provided."
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": f"{self.anthropic_api_key}",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-opus-20240229",  # Using Claude 3 for medical understanding
            "max_tokens": 1024,
            "messages": [
                {"role": "system", "content": "You are a clinical research assistant helping doctors find relevant clinical trials for their patients. Provide accurate information based on clinical trial data and cite the appropriate NCT ID for your information."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3  # Lower temperature for more factual responses
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                return f"Error: API request failed with status code {response.status_code}. {response.text}"
                
        except Exception as e:
            return f"Error connecting to Anthropic API: {str(e)}"
    
    def extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """
        Extract potential filters from a user query.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary of extracted filters
        """
        filters = {}
        
        # Extract phase information
        phase_match = re.search(r'phase (\d+)', query.lower())
        if phase_match:
            filters['phase'] = f"PHASE{phase_match.group(1)}"
        
        # Extract gender filter
        if re.search(r'\b(male|men)\b', query.lower()) and not re.search(r'\b(female|women)\b', query.lower()):
            filters['gender'] = "MALE"
        elif re.search(r'\b(female|women)\b', query.lower()) and not re.search(r'\b(male|men)\b', query.lower()):
            filters['gender'] = "FEMALE"
        
        # Extract healthy volunteer information
        if re.search(r'\bhealthy volunteers\b', query.lower()):
            filters['healthy_volunteers'] = "yes"
        
        return filters
    
    def answer_question(self, user_query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Process a user question and generate an answer based on relevant clinical trials.
        
        Args:
            user_query: The user's question
            n_results: Number of results to retrieve from vector DB
            
        Returns:
            Dict containing answer and supporting evidence
        """
        # Extract potential filters from query
        filters = self.extract_filters_from_query(user_query)
        
        # Query the vector DB
        retrieval_results = self.vector_db.query(
            query_text=user_query,
            n_results=n_results * 2,  # Retrieve more results initially
            filters=filters
        )
        
        # Extract unique trials (avoid duplicate NCT IDs)
        unique_results = self.vector_db.extract_unique_trials(retrieval_results)
        unique_results = unique_results[:n_results]  # Limit to requested number
        
        # If no results found, return a message
        if not unique_results:
            return {
                "answer": "I couldn't find any clinical trials matching your query. Try using more general terms or different keywords.",
                "evidence": []
            }
        
        # Format the context for the LLM
        context = self._format_context_for_llm(unique_results)
        
        # Construct the prompt
        prompt = f"""
        You are a clinical research assistant helping doctors find relevant clinical trials for their patients.
        
        Here is the doctor's question:
        "{user_query}"
        
        Based on the following clinical trial information, please provide a helpful and accurate answer:
        
        {context}
        
        In your response:
        1. Directly address the doctor's question
        2. Cite specific trials using their NCT IDs
        3. Be concise but include important eligibility criteria
        4. If the available information is insufficient, acknowledge this
        """
        
        # Query the LLM (use OpenAI by default, fall back to Anthropic)
        if self.openai_api_key:
            llm_response = self.query_openai(prompt)
        elif self.anthropic_api_key:
            llm_response = self.query_anthropic(prompt)
        else:
            llm_response = "Error: No LLM API keys configured."
        
        # Create response object with answer and evidence
        response = {
            "answer": llm_response,
            "evidence": [
                {
                    "nct_id": result["metadata"]["nct_id"],
                    "title": result["metadata"]["title"],
                    "principal_investigator": result["metadata"]["principal_investigator"],
                    "phase": result["metadata"]["phase"],
                    "source_url": result["metadata"]["source_url"]
                }
                for result in unique_results
            ]
        }
        
        return response
