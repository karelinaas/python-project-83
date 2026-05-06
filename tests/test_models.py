import pytest

from page_analyzer.models import URL, UrlCheck
from tests.conftest import UniqueUrlMixin


class TestURLModel(UniqueUrlMixin):
    """Тесты для модели URL."""

    def test_table_name(self):
        """Тест имени таблицы."""
        assert URL().table_name == "urls"

    def test_check_exists_before_insert_success(self):
        """Тест проверки существования URL перед вставкой."""
        existing_url_name = self._get_unique_url()
        existing_url = URL().create({"name": existing_url_name})
        
        result = URL().check_exists_before_insert({"name": existing_url_name})
        
        assert result["name"] == existing_url_name
        assert result["id"] == existing_url["id"]

    def test_check_exists_before_insert_not_found(self):
        """Тест проверки несуществующего URL."""
        result = URL().check_exists_before_insert(
            {"name": self._get_unique_url()}
        )
        
        assert result is None

    def test_check_exists_before_insert_no_name(self):
        """Тест проверки без поля name."""
        existing_url_name = self._get_unique_url()
        URL().create({"name": existing_url_name})

        with pytest.raises(Exception, match="Model is unique by name"):
            URL().check_exists_before_insert({"url": existing_url_name})

    def test_create_with_existing_check(self):
        """Тест создания с проверкой существования."""
        existing_url_name = self._get_unique_url()
        existing_url = URL().create(
            {"name": existing_url_name},
            check_existing_entity=False,
        )
        
        result = URL().create(
            {"name": existing_url_name},
            check_existing_entity=True,
        )
        
        assert result["name"] == existing_url_name
        assert result["id"] == existing_url["id"]

    def test_create_without_existing_check(self):
        """Тест создания без проверки существования."""
        url_name = self._get_unique_url()
        
        result = URL().create(
            {"name": url_name},
            check_existing_entity=False,
        )
        
        assert result["name"] == url_name


class TestUrlCheckModel(UniqueUrlMixin):
    """Тесты для модели UrlCheck."""

    def test_table_name(self):
        """Тест имени таблицы."""
        assert UrlCheck().table_name == "url_checks"

    def test_create_url_check(self):
        """Тест создания проверки URL."""
        url = URL().create(
            {"name": self._get_unique_url()},
            check_existing_entity=False,
        )
        
        result = UrlCheck().create({
            "url_id": url["id"],
            "status_code": 200,
            "h1": "Test",
            "title": "Test",
            "description": "Test"
        })
        
        assert result["url_id"] == url["id"]
        assert result["status_code"] == 200
        assert result["h1"] == "Test"

    def test_filter_url_checks_by_url_id(self):
        """Тест фильтрации проверок по URL ID."""
        url = URL().create(
            {"name": self._get_unique_url()},
            check_existing_entity=False,
        )
        
        UrlCheck().create({
            "url_id": url["id"],
            "status_code": 200,
            "h1": "Test1",
            "title": "Test1",
            "description": "Test1"
        })
        UrlCheck().create({
            "url_id": url["id"],
            "status_code": 201,
            "h1": "Test2",
            "title": "Test2",
            "description": "Test2"
        })
        
        result = UrlCheck().filter({"url_id": url["id"]})
        
        assert len(result) == 2
        assert all(item["url_id"] == url["id"] for item in result)
