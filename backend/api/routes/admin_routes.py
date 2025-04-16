import logging
from flask import Blueprint, request, jsonify, Response
from typing import Dict, Any

from core.vector_db.base import VectorDB

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__)


def create_admin_routes(vector_db: VectorDB, database = None) -> Blueprint:
    """
    Create admin routes with dependency injection.
    
    Args:
        vector_db: Vector database instance
        
    Returns:
        Admin routes blueprint
    """
    
    @admin_bp.route('/api/health', methods=['GET'])
    def health_check() -> Response:
        """API health check endpoint."""
        return jsonify({"status": "ok", "message": "Clinical Trials API is running"})
    
    @admin_bp.route('/api/load_trials', methods=['POST'])
    def load_trials() -> Response:
        """Admin endpoint to load and index clinical trials."""
        try:
            data = request.json
            
            if not data or 'file_path' not in data:
                return jsonify({"error": "Missing required fields"}), 400
            
            file_path = data['file_path']
            file_type = data.get('file_type', 'json')
            
            # Load trials based on file type
            logger.info(f"Loading trials from {file_path} (type: {file_type})")
            
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
            logger.error(f"Error loading trials: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    return admin_bp
