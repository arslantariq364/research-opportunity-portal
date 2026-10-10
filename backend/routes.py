"""
API routes for University Research Opportunity Portal.
Phase 1: Scaffolding and health check endpoints.
Full CRUD operations will be implemented in Phase 2.
"""
from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify backend service status."""
    return jsonify({
        "status": "ok",
        "service": "University Research Opportunity Portal API",
        "phase": 1
    }), 200

# Full CRUD opportunity endpoints (GET, POST, PUT, DELETE) will be implemented in Phase 2
