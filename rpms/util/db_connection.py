import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("RPMS_DB_HOST", "localhost"),
    "port": int(os.getenv("RPMS_DB_PORT", "3306")),
    "user": os.getenv("RPMS_DB_USER", "root"),
    # Change as per your MySQL setup, or set the RPMS_DB_PASSWORD environment
    # variable so the password never has to be committed to GitHub.
    "password": os.getenv("RPMS_DB_PASSWORD", "root"),
    "database": os.getenv("RPMS_DB_NAME", "recruitment_portal"),
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        raise RuntimeError(f"Database connection failed: {exc}") from exc


@contextmanager
def transaction():
    """Yield a connection; commit on success, roll back on any error.

    Used when one business action must change several tables together
    (for example: create an offer AND update the application status).
    """
    con = get_connection()
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
