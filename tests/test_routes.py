import pytest
from unittest.mock import patch, MagicMock
from flask import flash
from page_analyzer.models import URL, UrlCheck


class TestRoutes:
    """Тесты для маршрутов приложения."""

    def test_index_route(self, client):
        """Тест главной страницы."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_add_url_success(self, client, mock_db_connection):
        """Тест успешного добавления нового URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = None
        
        mock_cursor.fetchone.side_effect = [
            None, {"id": 1, "name": "example.com"},
        ]
        
        response = client.post("/urls", data={"url": "https://example.com"})
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_add_url_existing(self, client, mock_db_connection):
        """Тест добавления существующего URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = {"id": 1, "name": "example.com"}
        
        response = client.post("/urls", data={"url": "https://example.com"})
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_add_url_validation_empty(self, client):
        """Тест валидации пустого URL."""
        response = client.post("/urls", data={"url": ''})
        
        assert response.status_code == 422
        assert "URL не может быть пустым" in response.data

    def test_add_url_validation_too_long(self, client):
        """Тест валидации слишком длинного URL."""
        long_url = "https://example.com/" + "a" * 250
        response = client.post("/urls", data={"url": long_url})
        
        assert response.status_code == 422
        assert "URL не должен превышать 255 символов" in response.data

    def test_add_url_validation_invalid(self, client):
        """Тест валидации некорректного URL."""
        response = client.post("/urls", data={"url": "not-an-url"})
        
        assert response.status_code == 422
        assert "Некорректный URL" in response.data

    def test_urls_list(self, client, mock_db_connection):
        """Тест отображения списка URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "example.com", "created_at": "2023-01-01"},
            {"id": 2, "name": "test.com", "created_at": "2023-01-02"}
        ]
        
        response = client.get("/urls")
        
        assert response.status_code == 200
        assert b"example.com" in response.data
        assert b"test.com" in response.data

    def test_show_url_success(self, client, mock_db_connection):
        """Тест отображения конкретного URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.side_effect = [
            {"id": 1, "name": "example.com", "created_at": "2023-01-01"},
            {
                "id": 1,
                "url_id": 1,
                "status_code": 200,
                "h1": "Test",
                "title": "Test",
                "description": "Test",
            },
        ]
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "url_id": 1,
                "status_code": 200,
                "h1": "Test",
                "title": "Test",
                "description": "Test",
            },
        ]
        
        response = client.get("/urls/1")
        
        assert response.status_code == 200
        assert b"example.com" in response.data

    def test_show_url_not_found(self, client, mock_db_connection):
        """Тест отображения несуществующего URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = None
        
        response = client.get("/urls/999")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls")

    @patch("requests.get")
    def test_create_check_success(
        self,
        mock_get,
        client,
        mock_db_connection,
        sample_html_content,
    ):
        """Тест успешной проверки URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        mock_cursor.fetchone.side_effect = [
            {"id": 1, "name": "example.com", "created_at": "2023-01-01"},
            {
                "id": 1,
                "url_id": 1,
                "status_code": 200,
                "h1": "Test H1 Header",
                "title": "Test Page Title",
                "description": "Test page description",
            },
        ]
        
        response = client.post("/urls/1/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("requests.get")
    def test_create_check_request_exception(
        self,
        mock_get,
        client,
        mock_db_connection,
    ):
        """Тест обработки исключения при запросе."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_get.side_effect = Exception("Network error")
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "example.com",
            "created_at": "2023-01-01",
        }
        
        response = client.post("/urls/1/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_create_check_url_not_found(self, client, mock_db_connection):
        """Тест проверки несуществующего URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.return_value = None
        
        response = client.post("/urls/999/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls")

    @patch("requests.get")
    def test_create_check_http_error(
        self,
        mock_get,
        client,
        mock_db_connection,
    ):
        """Тест обработки HTTP ошибки."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "example.com",
            "created_at": "2023-01-01",
        }
        
        response = client.post("/urls/1/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_url_normalization(self, client, mock_db_connection):
        """Тест нормализации URL при добавлении."""
        mock_conn, mock_cursor = mock_db_connection
        
        mock_cursor.fetchone.side_effect = [
            None, {"id": 1, "name": "example.com/path"},
        ]
        
        response = client.post(
            "/urls",
            data={"url": "https://example.com/path?query=param#fragment"},
        )
        
        assert response.status_code == 302
        mock_cursor.execute.assert_called()
        
        call_args = mock_cursor.execute.call_args_list
        insert_call = None
        for call in call_args:
            if "INSERT" in str(call[0][0]):
                insert_call = call
                break
        
        assert insert_call is not None
        assert "example.com/path" in str(insert_call[0][1])
