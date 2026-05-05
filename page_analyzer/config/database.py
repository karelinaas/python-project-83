import os
import sqlite3
from pathlib import Path
from typing import Union

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


def get_db_connection() -> Union[psycopg.Connection, sqlite3.Connection]:
    load_dotenv()
    
    if os.getenv("TESTING") == "true":
        db_path = os.getenv("TEST_DATABASE_PATH", ":memory:")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        _create_test_schema(conn)
        
        return conn
    
    database_url: str | None = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg.connect(database_url, row_factory=dict_row)


def _create_test_schema(conn: sqlite3.Connection):
    schema_path = (
        Path(__file__).parent.parent.parent / "tests" / "test_database.sql"
    )
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
