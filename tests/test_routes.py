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

    def test_add_url_success(self, client):
        """Тест успешного добавления нового URL."""
        response = client.post("/urls", data={"url": "https://example.com"})
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_add_url_existing(self, client):
        """Тест добавления существующего URL."""
        # First add a URL
        url_model = URL()
        url_model.create({"name": "example.com"}, check_existing_entity=False)
        
        # Try to add the same URL again
        response = client.post("/urls", data={"url": "https://example.com"})
        
        assert response.status_code == 302
        assert response.location.endswith("/urls/1")

    def test_add_url_validation_empty(self, client):
        """Тест валидации пустого URL."""
        response = client.post("/urls", data={"url": ''})
        
        assert response.status_code == 422
        assert "URL не может быть пустым" in response.data.decode('utf-8')

    def test_add_url_validation_too_long(self, client):
        """Тест валидации слишком длинного URL."""
        long_url = "https://example.com/" + "a" * 250
        response = client.post("/urls", data={"url": long_url})
        
        assert response.status_code == 422
        assert "URL не должен превышать 255 символов" in response.data.decode('utf-8')

    def test_add_url_validation_invalid(self, client):
        """Тест валидации некорректного URL."""
        response = client.post("/urls", data={"url": "not-an-url"})
        
        assert response.status_code == 422
        assert "Некорректный URL" in response.data.decode('utf-8')

    def test_urls_list(self, client):
        """Тест отображения списка URL."""
        # Create some test URLs
        url_model = URL()
        url_model.create({"name": "example.com"}, check_existing_entity=False)
        url_model.create({"name": "test.com"}, check_existing_entity=False)
        
        response = client.get("/urls")
        
        assert response.status_code == 200
        assert b"example.com" in response.data
        assert b"test.com" in response.data

    def test_show_url_success(self, client):
        """Тест отображения конкретного URL."""
        # Create a test URL
        url_model = URL()
        url = url_model.create({"name": "example.com"}, check_existing_entity=False)
        
        # Create a check for this URL
        check_model = UrlCheck()
        check_model.create({
            "url_id": url["id"],
            "status_code": 200,
            "h1": "Test",
            "title": "Test",
            "description": "Test"
        })
        
        response = client.get(f"/urls/{url['id']}")
        
        assert response.status_code == 302

    def test_show_url_not_found(self, client):
        """Тест отображения несуществующего URL."""
        response = client.get("/urls/999")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls")

    @patch("requests.get")
    def test_create_check_success(
        self,
        mock_get,
        client,
        sample_html_content,
    ):
        """Тест успешной проверки URL."""
        # Create a test URL
        url_model = URL()
        url = url_model.create({"name": "example.com"}, check_existing_entity=False)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post(f"/urls/{url['id']}/checks")
        
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("requests.get")
    def test_create_check_request_exception(
        self,
        mock_get,
        client,
    ):
        """Тест обработки исключения при запросе."""
        # Create a test URL
        url_model = URL()
        url = url_model.create({"name": "example.com"}, check_existing_entity=False)
        
        mock_get.side_effect = Exception("Network error")
        
        response = client.post(f"/urls/{url['id']}/checks")
        
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")

    def test_create_check_url_not_found(self, client):
        """Тест проверки несуществующего URL."""
        response = client.post("/urls/999/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls")

    @patch("requests.get")
    def test_create_check_http_error(
        self,
        mock_get,
        client,
    ):
        """Тест обработки HTTP ошибки."""
        # Create a test URL
        url_model = URL()
        url = url_model.create({"name": "example.com"}, check_existing_entity=False)
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        response = client.post(f"/urls/{url['id']}/checks")
        
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")

    def test_url_normalization(self, client):
        """Тест нормализации URL при добавлении."""
        response = client.post(
            "/urls",
            data={"url": "https://example.com/path?query=param#fragment"},
        )
        
        assert response.status_code == 302
