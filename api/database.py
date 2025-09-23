import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os

# Database connection parameters
DATABASE_CONFIG = {
    "host": "localhost",
    "database": "oceandb",  # Your database name
    "user": "postgres",      # Your PostgreSQL username
    "password": "root",  # Your PostgreSQL password
    "port": "5433"
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(cursor_factory=RealDictCursor, **DATABASE_CONFIG)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def get_cursor():
    """Get database cursor for queries"""
    conn = psycopg2.connect(cursor_factory=RealDictCursor, **DATABASE_CONFIG)
    return conn, conn.cursor()
