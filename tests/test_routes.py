from enum import unique
from unittest.mock import patch, MagicMock

import pytest

from page_analyzer.models import URL, UrlCheck
from tests.conftest import UniqueUrlMixin


class TestRoutes(UniqueUrlMixin):
    """Тесты для маршрутов приложения."""

    def test_index_route(self, client):
        """Тест главной страницы."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_add_url_success(self, client):
        """Тест успешного добавления нового URL."""
        url_name = self._get_unique_url()
        response = client.post("/urls", data={"url": f"https://{url_name}"})

        created_url = URL().get(url_name, "name")

        assert created_url is not None
        assert created_url["name"] == url_name
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{created_url['id']}")

    def test_add_url_existing(self, client):
        """Тест добавления существующего URL."""
        url_name = self._get_unique_url()
        url = URL().create({"name": url_name})
        
        response = client.post("/urls", data={"url": f"https://{url_name}"})
        
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")

    def test_add_url_validation_empty(self, client):
        """Тест валидации пустого URL."""
        response = client.post("/urls", data={"url": ""})
        
        assert response.status_code == 422
        assert "URL не может быть пустым" in response.data.decode("utf-8")

    def test_add_url_validation_too_long(self, client):
        """Тест валидации слишком длинного URL."""
        long_url = "https://example.com/" + "a" * 250
        response = client.post("/urls", data={"url": long_url})
        
        assert response.status_code == 422
        assert (
            "URL не должен превышать 255 символов"
            in response.data.decode('utf-8')
        )

    def test_add_url_validation_invalid(self, client):
        """Тест валидации некорректного URL."""
        response = client.post("/urls", data={"url": "not-an-url"})
        
        assert response.status_code == 422
        assert "Некорректный URL" in response.data.decode("utf-8")

    def test_urls_list(self, client):
        """Тест отображения списка URL."""
        test_url1 = self._get_unique_url()
        test_url2 = self._get_unique_url()

        URL().create({"name": test_url1}, check_existing_entity=False)
        URL().create({"name": test_url2}, check_existing_entity=False)
        
        response = client.get("/urls")
        
        response_data_decoded = response.data.decode("utf-8")

        assert response.status_code == 200
        assert test_url1 in response_data_decoded
        assert test_url2 in response_data_decoded

    def test_show_url_success(self, client):
        """Тест отображения конкретного URL."""
        test_url = self._get_unique_url()
        url = URL().create({"name": test_url}, check_existing_entity=False)
        
        h1 = "Suspendisse vel libero eu mi."
        title = "Pellentesque sit amet pretium turpis."
        description = "Nunc vel tellus suscipit, convallis."
        UrlCheck().create({
            "url_id": url["id"],
            "status_code": 200,
            "h1": h1,
            "title": title,
            "description": description,
        })
        
        response = client.get(f"/urls/{url['id']}")
        
        response_data_decoded = response.data.decode("utf-8")

        assert response.status_code == 200
        assert test_url in response_data_decoded
        assert h1 in response_data_decoded
        assert title in response_data_decoded
        assert description in response_data_decoded

    def test_show_url_not_found(self, client):
        """Тест отображения несуществующего URL."""
        response = client.get("/urls/99999")
        
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
        test_url = self._get_unique_url()
        url = URL().create({"name": test_url}, check_existing_entity=False)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = client.post(f"/urls/{url['id']}/checks")
        
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")
        mock_get.assert_called_once_with(f"https://{test_url}", timeout=10)

    @patch("requests.get")
    def test_create_check_request_exception(self, mock_get, client):
        """Тест обработки исключения при запросе."""
        url = URL().create(
            {"name": self._get_unique_url()},
            check_existing_entity=False,
        )

        error_message = "Network error"
        mock_get.side_effect = RuntimeError(error_message)

        with pytest.raises(RuntimeError) as excinfo:
            response = client.post(f"/urls/{url['id']}/checks")
            assert response.status_code == 302
            assert response.location.endswith(f"/urls/{url['id']}")

        assert error_message in str(excinfo.value)

    def test_create_check_url_not_found(self, client):
        """Тест проверки несуществующего URL."""
        response = client.post("/urls/999/checks")
        
        assert response.status_code == 302
        assert response.location.endswith("/urls")

    def test_url_normalization(self, client):
        """Тест нормализации URL при добавлении."""
        unique_url = self._get_unique_url()
        test_url = f"https://{unique_url}/path?query=param#fragmen"
        response = client.post("/urls", data={"url": test_url})

        url = URL().get(f"{unique_url}/path", "name")

        assert url is not None
        assert response.status_code == 302
        assert response.location.endswith(f"/urls/{url['id']}")
