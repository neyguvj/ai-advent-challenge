from flask import Blueprint, jsonify, request
from app.db.messages import (
    create_message,
    get_messages_by_session_id,
    delete_messages_by_session_id,
    create_messages,
)
from app.db.models import Role
from app.routes.utils import run_request

# Create a Flask Blueprint for message routes
messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/sessions/<string:session_id>/messages", methods=["POST"])
@run_request
def append_message(session_id):
    """Append a new message to a session"""
    data = request.get_json()

    # Validate required fields
    if not data or "role" not in data or "content" not in data:
        return jsonify({"error": "Role and content are required"}), 400

    role = data["role"]
    content = data["content"]

    # Validate that the role is valid
    try:
        role_enum = Role(role)
    except ValueError:
        return (
            jsonify({"error": "Invalid role. Must be one of: system, assistent, user"}),
            400,
        )

    # Create the message
    try:
        message = create_message(session_id, role_enum, content)
        return jsonify(message), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create message: {str(e)}"}), 500


@messages_bp.route("/sessions/<string:session_id>/messages", methods=["GET"])
@run_request
def get_messages(session_id):
    """Get all messages for a specific session"""
    messages = get_messages_by_session_id(session_id)
    return jsonify([message.to_dict() for message in messages])


@messages_bp.route("/sessions/<string:session_id>/messages", methods=["DELETE"])
@run_request
def delete_messages(session_id):
    """Delete all messages for a specific session"""
    try:
        deleted_count = delete_messages_by_session_id(session_id)
        return jsonify(
            {
                "message": f"Successfully deleted {deleted_count} messages",
                "count": deleted_count,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to delete messages: {str(e)}"}), 500


@messages_bp.route("/sessions/<string:session_id>/messages/batch", methods=["POST"])
@run_request
def append_messages(session_id):
    """Append multiple messages to a session"""
    data = request.get_json()

    # Validate required fields
    if not data or "messages" not in data:
        return jsonify({"error": "Messages array is required"}), 400

    messages_data = data["messages"]

    # Validate that each message has required fields
    for i, msg in enumerate(messages_data):
        if "role" not in msg or "content" not in msg:
            return jsonify({"error": f"Message {i} is missing role or content"}), 400

    # Validate that the roles are valid
    for i, msg in enumerate(messages_data):
        try:
            Role(msg["role"])
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f"Invalid role in message {i}. Must be one of: system, assistent, user"
                    }
                ),
                400,
            )

    # Create the messages
    try:
        created_messages = create_messages(session_id, messages_data)
        return jsonify([msg.to_dict() for msg in created_messages]), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create messages: {str(e)}"}), 500
