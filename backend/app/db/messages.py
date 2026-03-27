from app.db import get_connection

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory


def get_messages_by_session_id(session_id: str) -> list[BaseMessage]:
    """Get all messages for a specific session from the database"""
    history = get_history_by_session_id(session_id)
    return history.messages


def delete_messages_by_session_id(session_id: str) -> int:
    """Delete all messages for a specific session from the database"""
    history = get_history_by_session_id(session_id)
    messages = history.messages
    count = len(messages)
    history.clear()
    return count


def get_history_by_session_id(session_id) -> BaseChatMessageHistory:
    history = PostgresChatMessageHistory(
        "chat_history",
        session_id,
        sync_connection=get_connection(),
    )
    return history
