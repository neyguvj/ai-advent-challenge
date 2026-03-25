from flask import Blueprint, jsonify

# Create a Flask Blueprint for health check
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint - returns empty successful response"""
    return jsonify({})
