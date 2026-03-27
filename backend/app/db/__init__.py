import os

import psycopg


def get_db_host():
    return os.getenv("PG_HOST")


def get_db_port():
    return os.getenv("PG_PORT")


def get_db_user():
    return os.getenv("PG_USER")


def get_db_password():
    return os.getenv("PG_PASSWORD")


def get_database():
    return os.getenv("PG_DATABASE")


def get_postgres_url():
    return f"postgresql://{get_db_user()}:{get_db_password()}@{get_db_host()}:{get_db_port()}/{get_database()}"


def get_psycopg_url():
    return f"postgresql+psycopg2://{get_db_user()}:{get_db_password()}@{get_db_host()}:{get_db_port()}/{get_database()}"


_conn = None


def get_connection():
    global _conn
    _conn = psycopg.connect(get_postgres_url(), autocommit=True)
    return _conn
