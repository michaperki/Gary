import logging
from typing import List, Dict, Any, Optional, Union

from core.llm.base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Responsible for generating responses to user queries based on retrieved trials.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the generator.
        
        Args:
            llm_provider: LLM provider to use for response generation
        """
        self.llm_provider = llm_provider
    
    def _format_context_for_llm(self, 
                                retrieval_results: List[Dict[str, Any]], 
                                verbose: bool = False) -> str:
        """
        Format the retrieved clinical trial information for the LLM prompt.
        
        Args:
            retrieval_results: Results from vector database query
            verbose: Whether to include more detailed information
            
        Returns:
            Formatted context string
        """
        if not retrieval_results:
            return "No clinical trial information available."
            
        context = "CLINICAL TRIAL INFORMATION:\n\n"
        
        for i, result in enumerate(retrieval_results):
            meta = result['metadata']
            context += f"[Trial {i+1}] {meta['title']}\n"
            context += f"NCT ID: {meta['nct_id']}\n"
            
            # Include more details in verbose mode
            if verbose:
                context += f"PI: {meta['principal_investigator']}\n"
                context += f"Phase: {meta['phase']}\n"
                context += f"Gender: {meta['gender']}\n"
                context += f"Age Range: {meta['age_range']}\n"
                context += f"Healthy Volunteers: {meta['healthy_volunteers']}\n"
            else:
                context += f"Phase: {meta['phase']}\n"
            
            context += f"Conditions: {meta['conditions']}\n"
            
            # Add the relevant chunk content
            content = result['text'].strip()
            context += f"Content: {content}\n\n"
        
        return context
    
    def generate_system_prompt(self, context: str) -> str:
        """
        Generate a system prompt for the LLM based on the context.
        
        Args:
            context: Formatted context string
            
        Returns:
            System prompt string
        """
        return f"""You are a helpful clinical trials assistant that helps healthcare professionals find relevant clinical trials for their patients.

Your goal is to provide specific, actionable information about clinical trials based ONLY on the trial data provided below.

IMPORTANT INSTRUCTIONS:
1. Answer using ONLY the information in the trials provided below.
2. Cite specific trials by NCT ID when discussing them.
3. If the trials contain relevant information, summarize the key eligibility criteria, phases, and interventions.
4. If the provided trials don't match the query well, acknowledge this and suggest what additional information would help.
5. Don't apologize or refuse to answer - if you have relevant trials, share the information directly.
6. Use a professional, helpful tone appropriate for medical professionals.

Here are the clinical trials available to answer this query:

{context}

IMPORTANT: Base your entire response on the trial information above. Be specific about what trials are available rather than asking for more information, unless absolutely necessary."""
    
    def generate_response(self, 
                          query: str, 
                          retrieval_results: List[Dict[str, Any]],
                          conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Generate a response to a user query based on retrieved trials.
        
        Args:
            query: User query string
            retrieval_results: Results from retrieval
            conversation_history: Optional conversation history
            
        Returns:
            Dictionary containing response and evidence
        """
        if not retrieval_results:
            return {
                "response": (
                    f"I couldn't find any clinical trials matching your query about '{query}'. "
                    f"This could be because we don't have trials on this topic, or the query needs to be more specific. "
                    f"Please try refining your search with more details like the specific condition, treatment history, or phase."
                ),
                "evidence": []
            }
        
        # Format context for LLM
        context = self._format_context_for_llm(retrieval_results)
        
        # Generate system prompt
        system_prompt = self.generate_system_prompt(context)
        
        # Prepare conversation history for LLM
        formatted_history = []
        if conversation_history:
            # Only use the last few messages to avoid context length issues
            recent_history = conversation_history[-5:]
            for msg in recent_history:
                formatted_history.append(msg)
        
        # Generate response using LLM
        response_text = self.llm_provider.generate_response(
            prompt=query,
            system_message=system_prompt,
            conversation_history=formatted_history,
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=800
        )
        
        # Format evidence for response
        evidence = []
        for result in retrieval_results:
            evidence.append({
                "nct_id": result["metadata"]["nct_id"],
                "title": result["metadata"]["title"],
                "principal_investigator": result["metadata"]["principal_investigator"],
                "phase": result["metadata"]["phase"],
                "source_url": result["metadata"]["source_url"]
            })
        
        return {
            "response": response_text,
            "evidence": evidence
        }
