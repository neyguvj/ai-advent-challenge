from flask import Blueprint, jsonify, request
from app.db.messages import (
    get_messages_by_session_id,
    delete_messages_by_session_id,
)
from app.routes.utils import run_request

# Create a Flask Blueprint for message routes
messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/sessions/<string:session_id>/messages", methods=["GET"])
@run_request
def get_messages(session_id):
    """Get all messages for a specific session"""
    messages = get_messages_by_session_id(session_id)
    return jsonify(
        [{"role": message.type, "content": message.content} for message in messages]
    )


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
