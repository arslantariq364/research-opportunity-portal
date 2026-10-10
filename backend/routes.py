"""
RESTful API routes for University Research Opportunity Portal.
Phase 2: Complete CRUD implementation for Research Opportunities.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

try:
    from backend.models import db, ResearchOpportunity
    from backend.validators import validate_create_opportunity, validate_update_opportunity
except ImportError:
    from models import db, ResearchOpportunity
    from validators import validate_create_opportunity, validate_update_opportunity

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify backend service status."""
    return jsonify({
        "status": "ok",
        "service": "University Research Opportunity Portal API",
        "phase": 2
    }), 200


@api_bp.route('/opportunities', methods=['POST'])
def create_opportunity():
    """
    Create a new research opportunity.
    Endpoint: POST /api/opportunities
    Status codes: 201 Created, 400 Bad Request, 500 Internal Server Error
    """
    if not request.is_json and request.content_type != 'application/json':
        # Check if json can still be parsed or if body is not JSON
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                "error": "Invalid request. Content-Type must be application/json with a valid JSON body."
            }), 400
    else:
        data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Malformed or invalid JSON payload."}), 400

    is_valid, cleaned_data, errors = validate_create_opportunity(data)
    if not is_valid:
        return jsonify({
            "error": "Validation failed",
            "messages": errors
        }), 400

    try:
        opportunity = ResearchOpportunity(**cleaned_data)
        db.session.add(opportunity)
        db.session.commit()
        return jsonify(opportunity.to_dict()), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "A database error occurred while creating the opportunity."}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected server error occurred."}), 500


@api_bp.route('/opportunities', methods=['GET'])
def get_all_opportunities():
    """
    Retrieve all research opportunities (Open and Closed).
    Endpoint: GET /api/opportunities
    Status codes: 200 OK, 500 Internal Server Error
    """
    try:
        opportunities = ResearchOpportunity.query.order_by(ResearchOpportunity.id.asc()).all()
        return jsonify([opp.to_dict() for opp in opportunities]), 200
    except SQLAlchemyError:
        return jsonify({"error": "A database error occurred while fetching opportunities."}), 500
    except Exception:
        return jsonify({"error": "An unexpected server error occurred."}), 500


@api_bp.route('/opportunities/<opportunity_id>', methods=['GET'])
def get_opportunity_by_id(opportunity_id):
    """
    Retrieve a specific research opportunity by its ID.
    Endpoint: GET /api/opportunities/<id>
    Status codes: 200 OK, 404 Not Found, 500 Internal Server Error
    """
    try:
        opp_id = int(opportunity_id)
        if opp_id <= 0:
            return jsonify({"error": "Research opportunity not found"}), 404
    except (ValueError, TypeError):
        return jsonify({"error": "Research opportunity not found"}), 404

    try:
        opportunity = db.session.get(ResearchOpportunity, opp_id)
        if not opportunity:
            return jsonify({"error": "Research opportunity not found"}), 404
        return jsonify(opportunity.to_dict()), 200
    except SQLAlchemyError:
        return jsonify({"error": "A database error occurred while retrieving the opportunity."}), 500
    except Exception:
        return jsonify({"error": "An unexpected server error occurred."}), 500


@api_bp.route('/opportunities/<opportunity_id>', methods=['PUT'])
def update_opportunity(opportunity_id):
    """
    Update an existing research opportunity with partial or full field updates.
    Endpoint: PUT /api/opportunities/<id>
    Status codes: 200 OK, 400 Bad Request, 404 Not Found, 500 Internal Server Error
    """
    try:
        opp_id = int(opportunity_id)
        if opp_id <= 0:
            return jsonify({"error": "Research opportunity not found"}), 404
    except (ValueError, TypeError):
        return jsonify({"error": "Research opportunity not found"}), 404

    opportunity = db.session.get(ResearchOpportunity, opp_id)
    if not opportunity:
        return jsonify({"error": "Research opportunity not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed or invalid JSON payload."}), 400

    is_valid, cleaned_data, errors = validate_update_opportunity(data)
    if not is_valid:
        return jsonify({
            "error": "Validation failed",
            "messages": errors
        }), 400

    try:
        for field, value in cleaned_data.items():
            setattr(opportunity, field, value)
        db.session.commit()
        return jsonify(opportunity.to_dict()), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "A database error occurred while updating the opportunity."}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected server error occurred."}), 500


@api_bp.route('/opportunities/<opportunity_id>', methods=['DELETE'])
def delete_opportunity(opportunity_id):
    """
    Delete a specific research opportunity by its ID.
    Endpoint: DELETE /api/opportunities/<id>
    Status codes: 200 OK, 404 Not Found, 500 Internal Server Error
    """
    try:
        opp_id = int(opportunity_id)
        if opp_id <= 0:
            return jsonify({"error": "Research opportunity not found"}), 404
    except (ValueError, TypeError):
        return jsonify({"error": "Research opportunity not found"}), 404

    opportunity = db.session.get(ResearchOpportunity, opp_id)
    if not opportunity:
        return jsonify({"error": "Research opportunity not found"}), 404

    try:
        db.session.delete(opportunity)
        db.session.commit()
        return jsonify({"message": "Research opportunity deleted successfully"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "A database error occurred while deleting the opportunity."}), 500
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected server error occurred."}), 500
