from flask import Blueprint, jsonify, request
from app.db.sessions import (
    get_sessions_by_user_id,
    get_session_by_id,
    delete_session_by_id,
    create_session,
    user_exists,
)
from app.db.models import Session
from app.routes.utils import run_request

# Create a Flask Blueprint for session routes
sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions", methods=["GET"])
@run_request
def list_sessions():
    """List all sessions"""
    sessions = get_sessions_by_user_id()
    return jsonify([session.to_dict() for session in sessions])


@sessions_bp.route("/sessions/<string:session_id>", methods=["GET"])
@run_request
def get_session(session_id):
    """Get a session by ID"""
    session = get_session_by_id(session_id)
    if session:
        return jsonify(session.to_dict())
    else:
        return jsonify({"error": "Session not found"}), 404


@sessions_bp.route("/sessions/<string:session_id>", methods=["DELETE"])
@run_request
def delete_session(session_id):
    """Delete a session by ID"""
    deleted = delete_session_by_id(session_id)
    if deleted:
        return jsonify({"message": "Session deleted successfully"})
    else:
        return jsonify({"error": "Session not found"}), 404


@sessions_bp.route("/users/<string:user_id>/sessions", methods=["GET"])
@run_request
def list_user_sessions(user_id):
    """List all sessions for a specific user"""
    sessions = get_sessions_by_user_id(user_id)
    return jsonify([session.to_dict() for session in sessions])


@sessions_bp.route("/users/<string:user_id>/sessions", methods=["POST"])
@run_request
def create_session_endpoint(user_id):
    """Create a new session for a user"""
    data = request.get_json()

    # Validate required fields
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    name = data["name"]

    # Validate that the user exists
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    # Create the session
    session = create_session(user_id, name)
    return jsonify(session.to_dict()), 201
