import os
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row


def get_db_connection() -> psycopg.Connection:
    database_url: str | None = os.environ.get("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg.connect(database_url, row_factory=dict_row)


class URL:
    @staticmethod
    def find_by_name(name: str) -> psycopg.rows.Row | None:
        """Найти URL по имени"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                return cur.fetchone()

    @staticmethod
    def find_by_id(url_id: int) -> psycopg.rows.Row | None:
        """Найти URL по ID"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                return cur.fetchone()

    @staticmethod
    def create(name: str) -> psycopg.rows.Row | None:
        """Создать новый URL"""
        # Нормализуем имя сайта
        parsed = urlparse(name)
        normalized_name = f"{parsed.scheme}://{parsed.netloc}"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Проверяем, существует ли уже такой URL
                cur.execute("SELECT * FROM urls WHERE name = %s", (normalized_name,))
                existing = cur.fetchone()
                if existing:
                    return existing
                
                # Создаем новую запись
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (normalized_name,)
                )
                url_id = cur.fetchone()['id']
                conn.commit()
                return URL.find_by_id(url_id)

    @staticmethod
    def get_all() -> list[psycopg.rows.Row] | None:
        """Получить все URL, отсортированные по created_at DESC"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls ORDER BY created_at DESC"
                )
                return cur.fetchall()
