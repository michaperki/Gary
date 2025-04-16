# clinical_trials_api.py
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import time
from typing import Dict, Any, List, Optional
import openai
from dotenv import load_dotenv

# Import our MinimalVectorDB instead
from minimal_vector_db import MinimalVectorDB

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], 
                           "allow_headers": ["Content-Type", "Authorization"]}})

# Initialize vector DB with minimal implementation
vector_db = MinimalVectorDB(db_directory="./vector_db")

# Keep a simple in-memory conversation history
conversations = {}

@app.route('/api/health', methods=['GET'])
def health_check() -> Response:
    """API health check endpoint."""
    return jsonify({"status": "ok", "message": "Clinical Trials API is running"})

@app.route('/api/trials/search', methods=['GET'])
def search_trials() -> Response:
    """Search for clinical trials using vector similarity."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        # Extract filters
        filters = {}
        for param in ['phase', 'gender', 'healthy_volunteers']:
            if param in request.args and request.args.get(param):
                filters[param] = request.args.get(param)
        
        # Query the vector DB
        results = vector_db.query(
            query_text=query,
            n_results=limit * 2,
            filters=filters
        )
        
        # Extract unique trials
        unique_results = vector_db.extract_unique_trials(results)
        unique_results = unique_results[:limit]
        
        # Format the results
        formatted_results = []
        for result in unique_results:
            formatted_results.append({
                "nct_id": result["metadata"]["nct_id"],
                "title": result["metadata"]["title"],
                "principal_investigator": result["metadata"]["principal_investigator"],
                "phase": result["metadata"]["phase"],
                "gender": result["metadata"]["gender"],
                "age_range": result["metadata"]["age_range"],
                "healthy_volunteers": result["metadata"]["healthy_volunteers"],
                "conditions": result["metadata"]["conditions"],
                "interventions": result["metadata"]["interventions"],
                "source_url": result["metadata"]["source_url"],
                "relevance_score": 1.0 - result["distance"] if result["distance"] is not None else None
            })
        
        return jsonify({
            "query": query,
            "filters": filters,
            "results": formatted_results,
            "total": len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trials/filters', methods=['GET'])
def get_filter_options() -> Response:
    """Get available filter options for the search interface."""
    try:
        filters = vector_db.get_filters_options()
        return jsonify(filters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/test_query', methods=['GET'])
def test_query() -> Response:
    """Debug endpoint to test vector search queries directly."""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Query the vector DB directly
        print(f"Testing query: {query}")
        results = vector_db.query(
            query_text=query,
            n_results=limit,
            filters={}
        )
        
        # Format the results for debugging
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.get("id", "unknown"),
                "distance": result.get("distance"),
                "metadata": result.get("metadata", {}),
                "text_sample": result.get("text", "")[:300] + "..." if len(result.get("text", "")) > 300 else result.get("text", "")
            })
        
        return jsonify({
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/vector_db', methods=['GET'])
def debug_vector_db() -> Response:
    """Debug endpoint to check vector database content."""
    try:
        # Get a sample of documents from the vector DB
        sample_size = min(20, len(vector_db.documents) if hasattr(vector_db, 'documents') else 0)
        
        if sample_size == 0:
            return jsonify({
                "error": "No documents found in the vector database",
                "indexed": False,
                "collection_size": 0
            }), 404
        
        # Get random sample indices
        import random
        sample_indices = random.sample(range(len(vector_db.documents)), sample_size)
        
        # Get sample documents
        sample_docs = []
        for idx in sample_indices:
            sample_docs.append({
                "id": vector_db.document_ids[idx] if hasattr(vector_db, 'document_ids') else "unknown",
                "text_sample": vector_db.documents[idx][:300] + "..." if len(vector_db.documents[idx]) > 300 else vector_db.documents[idx],
                "metadata": vector_db.metadatas[idx] if hasattr(vector_db, 'metadatas') else {}
            })
        
        # Get counts of document types
        metadata_stats = {}
        if hasattr(vector_db, 'metadatas'):
            for metadata in vector_db.metadatas:
                chunk_type = metadata.get('chunk_type', 'unknown')
                if chunk_type not in metadata_stats:
                    metadata_stats[chunk_type] = 0
                metadata_stats[chunk_type] += 1
        
        return jsonify({
            "indexed": True,
            "collection_size": len(vector_db.documents) if hasattr(vector_db, 'documents') else 0,
            "metadata_stats": metadata_stats,
            "sample_documents": sample_docs
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat() -> Response:
    """Chat endpoint to handle conversation with GPT and vector search."""
    # Handle preflight OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        message = data['message']
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id', 'anonymous')
        
        # If no conversation_id, create a new one
        if not conversation_id:
            conversation_id = f"conv_{int(time.time())}_{user_id}"
            conversations[conversation_id] = []
        
        # Add the message to conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            "role": "user",
            "content": message
        })
        
        # Get the conversation history (limited to last 10 messages for context)
        conversation_history = conversations[conversation_id][-10:]  # Limit context
        
        # Enhance query with medical terms
        # This helps with matching clinical terms in the vector search
        enhanced_query = message
        
        # Add more results for better coverage
        search_results = vector_db.query(
            query_text=enhanced_query,
            n_results=10,  # Get more results to increase chances of finding relevant trials
            filters={}
        )
        
        # Extract unique trials to use as evidence
        evidence = []
        unique_trials = vector_db.extract_unique_trials(search_results)
        
        # Check if we actually found any trials
        if not unique_trials:
            # No trials found - return a helpful message
            response_text = (
                f"I couldn't find any clinical trials in our database matching your query about '{message}'. "
                f"This could be because we don't have trials on this topic, or the query needs to be more specific. "
                f"Please try refining your search with more details like the specific condition, treatment history, or phase."
            )
            
            conversations[conversation_id].append({
                "role": "assistant",
                "content": response_text,
                "evidence": []
            })
            
            return jsonify({
                "response": response_text,
                "conversation_id": conversation_id,
                "evidence": []
            })
            
        # Select the top trials (more if available)
        top_trials = unique_trials[:5]  # Use up to 5 trials for more complete information
        
        for trial in top_trials:
            evidence.append({
                "nct_id": trial["metadata"]["nct_id"],
                "title": trial["metadata"]["title"],
                "source_url": trial["metadata"]["source_url"],
                "text": trial["text"][:800]  # Include more text for better context
            })
        
        # Prepare context for GPT with more specific instructions
        system_prompt = """You are a helpful clinical trials assistant that helps healthcare professionals find relevant clinical trials for their patients.

Your goal is to provide specific, actionable information about clinical trials based ONLY on the trial data provided below.

IMPORTANT INSTRUCTIONS:
1. Answer using ONLY the information in the trials provided below.
2. Cite specific trials by NCT ID when discussing them.
3. If the trials contain relevant information, summarize the key eligibility criteria, phases, and interventions.
4. If the provided trials don't match the query well, acknowledge this and suggest what additional information would help.
5. Don't apologize or refuse to answer - if you have relevant trials, share the information directly.
6. Use a professional, helpful tone appropriate for medical professionals.

Here are the clinical trials available to answer this query:

"""
        
        for i, trial in enumerate(evidence):
            system_prompt += f"TRIAL {i+1}:\n"
            system_prompt += f"NCT ID: {trial['nct_id']}\n"
            system_prompt += f"TITLE: {trial['title']}\n"
            system_prompt += f"TEXT: {trial['text']}\n\n"
        
        # Add a final instruction to emphasize using the trial data
        system_prompt += "\nIMPORTANT: Base your entire response on the trial information above. Be specific about what trials are available rather than asking for more information, unless absolutely necessary."
        
        # Prepare messages for GPT
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last few messages for context)
        for msg in conversation_history[-5:]:  # Just the most recent messages
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Call GPT API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,  # Lower temperature for more factual responses
            max_tokens=800
        )
        
        # Extract response text
        response_text = response.choices[0].message.content
        
        # Add the assistant response to conversation history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text,
            "evidence": evidence
        })
        
        # Format evidence for response (remove the text to reduce payload size)
        evidence_response = []
        for trial in evidence:
            evidence_response.append({
                "nct_id": trial["nct_id"],
                "title": trial["title"],
                "source_url": trial["source_url"]
            })
        
        return jsonify({
            "response": response_text,
            "conversation_id": conversation_id,
            "evidence": evidence_response
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id: str) -> Response:
    """Get the history of a specific conversation."""
    try:
        if conversation_id not in conversations:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify({
            "conversation_id": conversation_id,
            "messages": conversations[conversation_id]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_trials', methods=['POST'])
def load_trials() -> Response:
    """Admin endpoint to load and index clinical trials."""
    try:
        data = request.json
        
        if not data or 'file_path' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        file_path = data['file_path']
        file_type = data.get('file_type', 'json')
        
        # Load trials based on file type
        if file_type.lower() == 'json':
            trials = vector_db.load_trials_from_json(file_path)
        elif file_type.lower() == 'csv':
            trials = vector_db.load_trials_from_csv(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
        
        # Process and index trials
        vector_db.process_and_index_trials(trials)
        
        return jsonify({
            "status": "success",
            "message": f"Loaded and indexed {len(trials)} clinical trials"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
