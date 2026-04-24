import os
from urllib.parse import urlparse

import psycopg
from psycopg.rows import dict_row


def get_db_connection():
    return psycopg.connect(os.getenv("DATABASE_URL"), row_factory=dict_row)


class URL:
    @staticmethod
    def find_by_name(name):
        """Найти URL по имени"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                return cur.fetchone()

    @staticmethod
    def find_by_id(url_id):
        """Найти URL по ID"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                return cur.fetchone()

    @staticmethod
    def create(name):
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
    def get_all():
        """Получить все URL, отсортированные по created_at DESC"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls ORDER BY created_at DESC"
                )
                return cur.fetchall()
