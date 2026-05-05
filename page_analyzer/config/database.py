import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Union

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


def get_db_connection() -> Union[psycopg.Connection, sqlite3.Connection]:
    load_dotenv()
    
    # Check if we're in test mode
    if os.getenv("TESTING") == "true":
        # Use SQLite for testing
        db_path = os.getenv("TEST_DATABASE_PATH", ":memory:")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Create schema if it doesn't exist
        _create_test_schema(conn)
        
        return conn
    
    # Use PostgreSQL for production
    database_url: str | None = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg.connect(database_url, row_factory=dict_row)


def _create_test_schema(conn: sqlite3.Connection):
    """Create test database schema if tables don't exist."""
    cursor = conn.cursor()
    
    # Check if tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if 'urls' not in existing_tables:
        # Read and execute test database schema
        schema_path = Path(__file__).parent.parent.parent / "tests" / "test_database.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()


@contextmanager
def get_test_db_connection():
    """Context manager for test database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
