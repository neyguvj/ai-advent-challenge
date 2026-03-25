from sqlalchemy.orm import sessionmaker
from app.db.models import User
from app.db import get_url
from sqlalchemy import create_engine
import uuid

# Create engine and session factory once when the module is loaded
engine = create_engine(get_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_user(email: str, password: str) -> User:
    """Create a new user in the database"""
    db_session = SessionLocal()
    try:
        # Generate UUID for new user
        user_id = str(uuid.uuid4())

        # Create the user object
        db_user = User(id=user_id, email=email, password=password)

        # Add to session and commit
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)

        return db_user
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def get_user_by_id(user_id: str) -> User | None:
    """Get a user by ID from the database"""
    db_session = SessionLocal()
    try:
        return db_session.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise e
    finally:
        db_session.close()


def get_all_users() -> list[User]:
    """Get all users from the database"""
    db_session = SessionLocal()
    try:
        return db_session.query(User).all()
    except Exception as e:
        raise e
    finally:
        db_session.close()


def delete_user_by_id(user_id: str) -> bool:
    """Delete a user by ID from the database"""
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            db_session.delete(user)
            db_session.commit()
            return True
        return False
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()


def get_user_by_email(email: str) -> User | None:
    """Get a user by email from the database"""
    db_session = SessionLocal()
    try:
        return db_session.query(User).filter(User.email == email).first()
    except Exception as e:
        raise e
    finally:
        db_session.close()
