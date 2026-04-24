from psycopg.rows import Row

from page_analyzer.config.database import get_db_connection


class URL:
    @staticmethod
    def find_by_name(name: str) -> Row | None:
        """Найти URL по имени"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                return cur.fetchone()

    @staticmethod
    def find_by_id(url_id: int) -> Row | None:
        """Найти URL по ID"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                return cur.fetchone()

    @staticmethod
    def create(name: str) -> Row | None:
        """Создать новый URL"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Проверяем, существует ли уже такой URL
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                existing = cur.fetchone()
                if existing:
                    return existing
                
                # Создаем новую запись
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (name,)
                )
                url_id = cur.fetchone()['id']
                conn.commit()
                return URL.find_by_id(url_id)

    @staticmethod
    def get_all() -> list[Row] | None:
        """Получить все URL, отсортированные по created_at DESC"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls ORDER BY created_at DESC"
                )
                return cur.fetchall()


class UrlCheck:
    @staticmethod
    def create(url_id: int) -> Row | None:
        """Создать новую проверку URL"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        "INSERT INTO url_checks (url_id) VALUES (%s) RETURNING id, created_at",
                        (url_id,)
                    )
                    result = cur.fetchone()
                    conn.commit()
                    return result
                except Exception:
                    conn.rollback()
                    return None

    @staticmethod
    def get_by_url_id(url_id: int) -> list[Row] | None:
        """Получить все проверки для конкретного URL"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, status_code, h1, title, description, created_at 
                    FROM url_checks 
                    WHERE url_id = %s 
                    ORDER BY created_at DESC
                """, (url_id,))
                return cur.fetchall()
    @staticmethod
    def find_by_name(name: str) -> Row | None:
        """Найти URL по имени"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                return cur.fetchone()

    @staticmethod
    def find_by_id(url_id: int) -> Row | None:
        """Найти URL по ID"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                return cur.fetchone()

    @staticmethod
    def create(name: str) -> Row | None:
        """Создать новый URL"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Проверяем, существует ли уже такой URL
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                existing = cur.fetchone()
                if existing:
                    return existing
                
                # Создаем новую запись
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (name,)
                )
                url_id = cur.fetchone()['id']
                conn.commit()
                return URL.find_by_id(url_id)

    @staticmethod
    def get_all() -> list[Row] | None:
        """Получить все URL с последними проверками, отсортированные по created_at DESC"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.*, 
                           (SELECT created_at FROM url_checks 
                            WHERE url_id = u.id 
                            ORDER BY created_at DESC LIMIT 1) as last_check_date
                    FROM urls u 
                    ORDER BY u.created_at DESC
                """)
                return cur.fetchall()
