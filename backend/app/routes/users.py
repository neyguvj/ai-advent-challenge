from flask import Blueprint, jsonify, request
from app.db.users import (
    get_all_users,
    get_user_by_id,
    delete_user_by_id,
    create_user,
    get_user_by_email,
)
from app.db.models import User
from app.routes.utils import run_request

# Create a Flask Blueprint for user routes
users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
@run_request
def list_users():
    """List all users"""
    users = get_all_users()
    return jsonify([user.to_dict() for user in users])


@users_bp.route("/users/<string:user_id>", methods=["GET"])
@run_request
def get_user(user_id):
    """Get a user by ID"""
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404


@users_bp.route("/users/<string:user_id>", methods=["DELETE"])
@run_request
def delete_user(user_id):
    """Delete a user by ID"""
    deleted = delete_user_by_id(user_id)
    if deleted:
        return jsonify({"message": "User deleted successfully"})
    else:
        return jsonify({"error": "User not found"}), 404


@users_bp.route("/users", methods=["POST"])
@run_request
def create_user_endpoint():
    """Create a new user"""
    data = request.get_json()

    # Validate required fields
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    # Create the user
    user = create_user(email, password)
    return jsonify(user.to_dict()), 201


@users_bp.route("/users/email/<string:email>", methods=["GET"])
@run_request
def get_user_id_by_email(email):
    """Get a user ID by email"""
    user = get_user_by_email(email)
    if user:
        return jsonify({"id": user.id})
    else:
        return jsonify({"error": "User not found"}), 404
