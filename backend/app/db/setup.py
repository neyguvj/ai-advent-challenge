import psycopg

from app.db.checkpointer import get_checkpointer
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory

from app.db import get_postgres_url


def setup():
    with psycopg.connect(get_postgres_url(), autocommit=True) as conn:
        checkpointer = get_checkpointer(conn)
        checkpointer.setup()

        PostgresChatMessageHistory.create_tables(conn, "chat_history")
