from sqlalchemy.orm import sessionmaker
from app.db.models import Session
from app.db import get_psycopg_url
from app.db.users import get_user_by_id
from sqlalchemy import create_engine
import uuid

# Create engine and session factory once when the module is loaded
engine = create_engine(get_psycopg_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_session(user_id: str, name: str) -> Session:
    """Create a new session in the database"""
    db_session = SessionLocal()
    try:
        # Generate UUID for new session
        session_id = str(uuid.uuid4())

        # Create the session object
        db_session_obj = Session(id=session_id, user_id=user_id, name=name)

        # Add to session and commit
        db_session.add(db_session_obj)
        db_session.commit()
        db_session.refresh(db_session_obj)

        return db_session_obj
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def get_session_by_id(session_id: str) -> Session | None:
    """Get a session by ID from the database"""
    db_session = SessionLocal()
    try:
        return db_session.query(Session).filter(Session.id == session_id).first()
    except Exception as e:
        raise e
    finally:
        db_session.close()


def get_sessions_by_user_id(user_id: str | None = None) -> list[Session]:
    """Get all sessions for a specific user from the database, or all sessions if no user_id provided"""
    db_session = SessionLocal()
    try:
        if user_id is None:
            # Return all sessions
            return db_session.query(Session).all()
        else:
            # Return sessions for specific user
            return db_session.query(Session).filter(Session.user_id == user_id).all()
    except Exception as e:
        raise e
    finally:
        db_session.close()


def delete_session_by_id(session_id: str) -> bool:
    """Delete a session by ID from the database"""
    db_session = SessionLocal()
    try:
        session = db_session.query(Session).filter(Session.id == session_id).first()
        if session:
            db_session.delete(session)
            db_session.commit()
            return True
        return False
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def user_exists(user_id: str) -> bool:
    """Check if a user exists in the database"""
    user = get_user_by_id(user_id)
    return user is not None
