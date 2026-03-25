from sqlalchemy.orm import sessionmaker
from app.db.models import Message, Role
from app.db import get_url
from sqlalchemy import create_engine
import uuid
from datetime import datetime

# Create engine and session factory once when the module is loaded
engine = create_engine(get_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_message(session_id: str, role: Role, content: str) -> Message:
    """Create a new message in the database"""
    db_session = SessionLocal()
    try:
        # Generate UUID for new message
        message_id = str(uuid.uuid4())

        # Create the message object
        db_message = Message(
            id=message_id,
            session_id=session_id,
            timestamp=datetime.now(),
            role=role,
            content=content,
        )

        # Add to session and commit
        db_session.add(db_message)
        db_session.commit()
        db_session.refresh(db_message)

        return db_message
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def get_messages_by_session_id(session_id: str) -> list[Message]:
    """Get all messages for a specific session from the database"""
    db_session = SessionLocal()
    try:
        return db_session.query(Message).filter(Message.session_id == session_id).all()
    except Exception as e:
        raise e
    finally:
        db_session.close()


def delete_messages_by_session_id(session_id: str) -> int:
    """Delete all messages for a specific session from the database"""
    db_session = SessionLocal()
    try:
        messages = (
            db_session.query(Message).filter(Message.session_id == session_id).all()
        )
        deleted_count = len(messages)

        if messages:
            db_session.query(Message).filter(Message.session_id == session_id).delete(
                synchronize_session=False
            )
            db_session.commit()

        return deleted_count
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def create_messages(session_id: str, messages_data: list[dict]) -> list[Message]:
    """Create multiple messages in the database"""
    db_session = SessionLocal()
    created_messages = []

    try:
        for msg_data in messages_data:
            # Generate UUID for new message
            message_id = str(uuid.uuid4())

            # Create the message object
            db_message = Message(
                id=message_id,
                session_id=session_id,
                timestamp=datetime.now(),
                role=Role(msg_data["role"]),
                content=msg_data["content"],
            )

            # Add to session
            db_session.add(db_message)
            created_messages.append(db_message)

        # Commit all messages at once
        db_session.commit()

        # Refresh to get updated data (like generated IDs)
        for msg in created_messages:
            db_session.refresh(msg)

        return created_messages
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()
