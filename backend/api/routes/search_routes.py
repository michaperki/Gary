import logging
from flask import Blueprint, request, jsonify, Response
from typing import Dict, Any, Optional

from core.vector_db.base import VectorDB

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__)


def create_search_routes(vector_db: VectorDB, database = None) -> Blueprint:
    """
    Create search routes with dependency injection.
    
    Args:
        vector_db: Vector database instance
        
    Returns:
        Search routes blueprint
    """
    
    @search_bp.route('/api/trials/search', methods=['GET'])
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
            
            logger.info(f"Search query: '{query}', filters: {filters}")
            
            # Validate query
            if not query:
                return jsonify({"error": "Missing query parameter 'q'"}), 400
            
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
            
            logger.info(f"Returning {len(formatted_results)} results for query: '{query}'")
            
            return jsonify({
                "query": query,
                "filters": filters,
                "results": formatted_results,
                "total": len(formatted_results)
            })
        
        except Exception as e:
            logger.error(f"Error in search endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    @search_bp.route('/api/trials/filters', methods=['GET'])
    def get_filter_options() -> Response:
        """Get available filter options for the search interface."""
        try:
            filters = vector_db.get_filters_options()
            return jsonify(filters)
        except Exception as e:
            logger.error(f"Error in filters endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    @search_bp.route('/api/debug/test_query', methods=['GET'])
    def test_query() -> Response:
        """Debug endpoint to test vector search queries directly."""
        try:
            query = request.args.get('q', '')
            limit = int(request.args.get('limit', 10))
            
            if not query:
                return jsonify({"error": "No query provided"}), 400
            
            # Query the vector DB directly
            logger.info(f"Testing query: {query}")
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
            logger.error(f"Error in test_query endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    @search_bp.route('/api/debug/vector_db', methods=['GET'])
    def debug_vector_db() -> Response:
        """Debug endpoint to check vector database content."""
        try:
            # Check if vector DB has documents
            if not hasattr(vector_db, 'documents') or not vector_db.documents:
                return jsonify({
                    "error": "No documents found in the vector database",
                    "indexed": False,
                    "collection_size": 0
                }), 404
            
            # Get a sample of documents from the vector DB
            sample_size = min(20, len(vector_db.documents))
            
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
                "collection_size": len(vector_db.documents),
                "metadata_stats": metadata_stats,
                "sample_documents": sample_docs
            })
        
        except Exception as e:
            logger.error(f"Error in debug_vector_db endpoint: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    return search_bp
