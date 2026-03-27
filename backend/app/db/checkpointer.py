from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

from app.db import get_postgres_url


def get_checkpointer(conn) -> PostgresSaver:
    checkpointer = PostgresSaver(conn)
    return checkpointer
