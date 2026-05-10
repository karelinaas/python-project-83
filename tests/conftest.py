import os
import sqlite3
import uuid
from pathlib import Path
from typing import Generator

import pytest

from page_analyzer.app import app
from page_analyzer.models import base


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    os.environ["TESTING"] = "true"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def client():
    """Создает тестовый клиент Flask-приложения."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    
    with app.test_client() as client:
        with app.app_context():
            yield client


def create_test_schema(conn: sqlite3.Connection):
    schema_path = (
        Path(__file__).parent / "test_database.sql"
    )
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()


@pytest.fixture(scope="session")
def shared_db_conn() -> Generator[sqlite3.Connection, None, None]:
    """
    Создает единое соединение с SQLite, которое живет всё время выполнения тестов.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    create_test_schema(conn)

    yield conn

    conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db_mock(shared_db_conn: sqlite3.Connection):
    """
    Подменяет функцию get_db_connection во всем приложении,
    чтобы она всегда возвращала готовое соединение.
    """
    mp = pytest.MonkeyPatch()
    mp.setattr(base, "get_db_connection", lambda: shared_db_conn)

    yield mp

    mp.undo()


@pytest.fixture
def sample_html_content():
    """Пример HTML-контента для тестов."""
    return """
    <html>
    <head>
        <title>Test Page Title</title>
        <meta name="description" content="Test page description">
    </head>
    <body>
        <h1>Test H1 Header</h1>
        <p>Test content</p>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_without_seo():
    """HTML-контент без SEO тегов для тестов."""
    return """
    <html>
    <head>
    </head>
    <body>
        <p>Test content without SEO tags</p>
    </body>
    </html>
    """


class UniqueUrlMixin:
    def _get_unique_url(self) -> str:
        return f"https://example.{uuid.uuid4()}.com"
