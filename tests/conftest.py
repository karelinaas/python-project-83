import os
import uuid
from unittest.mock import MagicMock

import pytest

from page_analyzer.app import app


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


@pytest.fixture
def mock_requests_response():
    """Мокирует ответ от requests.get."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = (
        "<html><head><title>Test</title></head><body>"
        "<h1>Header</h1></body></html>"
    )
    mock_response.raise_for_status.return_value = None
    return mock_response


class UniqueUrlMixin:
    def _get_unique_url(self) -> str:
        return f"example.{uuid.uuid4()}.com"
