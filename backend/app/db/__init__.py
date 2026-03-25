import os


def get_url():
    return "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
        os.getenv("PG_USER"),
        os.getenv("PG_PASSWORD"),
        os.getenv("PG_HOST"),
        os.getenv("PG_PORT"),
        os.getenv("PG_DATABASE"),
    )
