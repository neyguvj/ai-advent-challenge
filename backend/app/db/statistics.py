from sqlalchemy.orm import sessionmaker
from app.db.models import Statistics, User
from app.db import get_psycopg_url
from sqlalchemy import create_engine


# Create engine and session factory once when the module is loaded
engine = create_engine(get_psycopg_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_statistics_by_session_id(session_id: str) -> Statistics | None:
    """Get statistics for a session from the database"""
    db_session = SessionLocal()
    try:
        return (
            db_session.query(Statistics)
            .filter(Statistics.session_id == session_id)
            .first()
        )
    finally:
        db_session.close()


def update_statistics(
    session_id: str, input_tokens: int, output_tokens: int
) -> Statistics:
    """Update statistics for a session in the database"""
    db_session = SessionLocal()
    try:
        # Get existing statistics or create new one
        stats = (
            db_session.query(Statistics)
            .filter(Statistics.session_id == session_id)
            .first()
        )

        if not stats:
            # Create new statistics record
            stats = Statistics(
                session_id=session_id,
                total_input_tokens=0,
                total_output_tokens=0,
                last_input_tokens=0,
                last_output_tokens=0,
            )
            db_session.add(stats)

        # Update statistics
        stats.total_input_tokens += input_tokens
        stats.total_output_tokens += output_tokens
        stats.last_input_tokens = input_tokens
        stats.last_output_tokens = output_tokens
        db_session.commit()

        db_session.refresh(stats)
        return stats
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()
