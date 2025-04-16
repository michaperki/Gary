import logging
import time
from flask import Blueprint, request, jsonify, Response
from typing import Dict, Any, List, Optional

from rag import ClinicalTrialsRAG

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Keep a simple in-memory conversation history
conversations = {}


def create_chat_routes(rag_system: ClinicalTrialsRAG, database = None) -> Blueprint:
    """
    Create chat routes with dependency injection.
    
    Args:
        rag_system: RAG system instance
        database: Database instance for conversation storage (optional)
        
    Returns:
        Chat routes blueprint
    """
    
    @chat_bp.route('/api/chat', methods=['POST', 'OPTIONS'])
    def chat() -> Response:
        """Chat endpoint to handle conversation with RAG system."""
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
            
            # Get existing conversation or create new one
            if conversation_id in conversations:
                conversation_history = conversations[conversation_id]
            elif database is not None:
                # Try to get conversation from database
                stored_conversation = database.get_conversation(conversation_id)
                if stored_conversation:
                    conversation_history = stored_conversation.get('messages', [])
                else:
                    conversation_history = []
                    conversations[conversation_id] = conversation_history
            else:
                # Initialize new conversation
                conversation_history = []
                conversations[conversation_id] = conversation_history
            
            # Add the message to conversation history
            conversation_history.append({
                "role": "user",
                "content": message
            })
            
            # Process the query using the RAG system
            response_data = rag_system.answer_question(
                query=message,
                n_results=5,
                conversation_history=conversation_history
            )
            
            # Extract response and evidence
            response_text = response_data.get("response", "")
            evidence = response_data.get("evidence", [])
            
            # Add the assistant response to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "evidence": evidence
            })
            
            # Store the updated conversation
            conversations[conversation_id] = conversation_history
            
            # If database is available, store the conversation
            if database is not None:
                try:
                    database.store_conversation(
                        conversation_id=conversation_id,
                        messages=conversation_history,
                        user_id=user_id
                    )
                except Exception as e:
                    logger.error(f"Error storing conversation in database: {str(e)}", exc_info=True)
            
            # Format evidence for response (simplify metadata)
            evidence_response = []
            for trial in evidence:
                evidence_response.append({
                    "nct_id": trial.get("nct_id", ""),
                    "title": trial.get("title", ""),
                    "source_url": trial.get("source_url", "")
                })
            
            return jsonify({
                "response": response_text,
                "conversation_id": conversation_id,
                "evidence": evidence_response
            })
        
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    @chat_bp.route('/api/conversations/<conversation_id>', methods=['GET'])
    def get_conversation(conversation_id: str) -> Response:
        """Get the history of a specific conversation."""
        try:
            # First check in-memory conversations
            if conversation_id in conversations:
                return jsonify({
                    "conversation_id": conversation_id,
                    "messages": conversations[conversation_id]
                })
            
            # If not in memory and database is available, check database
            if database is not None:
                stored_conversation = database.get_conversation(conversation_id)
                if stored_conversation:
                    return jsonify({
                        "conversation_id": conversation_id,
                        "messages": stored_conversation.get('messages', [])
                    })
            
            # If conversation not found in either location
            return jsonify({"error": "Conversation not found"}), 404
        
        except Exception as e:
            logger.error(f"Error in get_conversation endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    # Return the blueprint - this line was missing
    return chat_bp
