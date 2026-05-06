import os
import sqlite3
from typing import Union

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


def get_db_connection() -> Union[psycopg.Connection, sqlite3.Connection]:
    load_dotenv()

    database_url: str | None = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg.connect(database_url, row_factory=dict_row)
