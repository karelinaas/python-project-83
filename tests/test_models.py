import pytest

from page_analyzer.models import URL, UrlCheck


class TestBaseModel:
    """Тесты для базовой модели."""

    def test_filter_single_condition(self, mock_db_connection):
        """Тест фильтрации с одним условием."""
        mock_conn, mock_cursor = mock_db_connection
        mock_name = "example.com"
        
        url_model = URL()
        mock_cursor.fetchone.return_value = {"id": 1, "name": mock_name}
        
        result = url_model.filter(
            {"name": mock_name},
            return_one_entity=True,
        )
        
        assert result["name"] == mock_name

    def test_filter_multiple_conditions(self, mock_db_connection):
        """Тест фильтрации с несколькими условиями."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "example.com"}
        ]
        
        result = url_model.filter({"name": "example.com", "id": 1})
        
        assert len(result) == 1
        assert result[0]["name"] == "example.com"

    def test_get_by_id(self, mock_db_connection):
        """Тест получения записи по ID."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "example.com"}
        
        result = url_model.get(1)
        
        assert result is not None
        assert result["name"] == "example.com"

    def test_get_by_column(self, mock_db_connection):
        """Тест получения записи по другому столбцу."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "example.com"}
        
        result = url_model.get("example.com", column="name")
        
        assert result["name"] == "example.com"

    def test_create_success(self, mock_db_connection):
        """Тест успешного создания записи."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.side_effect = [
            {"id": 1},
            {"id": 1, "name": "example.com", "created_at": "2023-01-01"},
        ]
        
        result = url_model.create({"name": "example.com"})
        
        assert result["name"] == "example.com"
        assert "created_at" in result
        
        calls = mock_cursor.execute.call_args_list
        assert len(calls) == 2
        assert "INSERT INTO urls" in str(calls[0][0][0])
        assert "SELECT * FROM urls WHERE id = %s" in str(calls[1][0][0])

    def test_get_all_default(self, mock_db_connection):
        """Тест получения всех записей без сортировки."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "example.com"},
            {"id": 2, "name": "test.com"}
        ]
        
        result = url_model.get_all()
        
        # Проверяем что мок был вызван и вернул наши данные
        assert mock_cursor.fetchall.called
        assert len(result) == 2

    def test_get_all_with_ordering(self, mock_db_connection):
        """Тест получения всех записей с сортировкой."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchall.return_value = [
            {"id": 2, "name": "test.com"},
            {"id": 1, "name": "example.com"}
        ]
        
        result = url_model.get_all(order_by=("created_at",), order_asc=False)
        
        assert mock_cursor.fetchall.called
        assert len(result) == 2

    def test_get_all_multiple_ordering(self, mock_db_connection):
        """Тест получения всех записей с множественной сортировкой."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchall.return_value = []
        
        url_model.get_all(order_by=("name", "created_at"), order_asc=True)
        
        
    def test_database_exception_handling(self, mock_db_connection):
        """Тест обработки исключений базы данных."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            url_model.get(1)
        
        

class TestURLModel:
    """Тесты для модели URL."""

    def test_table_name(self):
        """Тест имени таблицы."""
        url_model = URL()
        assert url_model.table_name == "urls"

    def test_check_exists_before_insert_success(self, mock_db_connection):
        """Тест проверки существования URL перед вставкой."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "example.com"}
        
        result = url_model.check_exists_before_insert({"name": "example.com"})
        
        assert result["name"] == "example.com"

    def test_check_exists_before_insert_not_found(self, mock_db_connection):
        """Тест проверки несуществующего URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.return_value = None
        
        result = url_model.check_exists_before_insert(
            {"name": "nonexistent.com"}
        )
        
        assert result is None

    def test_check_exists_before_insert_no_name(self, mock_db_connection):
        """Тест проверки без поля name."""
        url_model = URL()
        
        with pytest.raises(Exception, match="Model is unique by name"):
            url_model.check_exists_before_insert({"url": "example.com"})

    def test_create_with_existing_check(self, mock_db_connection):
        """Тест создания с проверкой существования."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "example.com"}
        
        result = url_model.create(
            {"name": "example.com"},
            check_existing_entity=True,
        )
        
        assert result["name"] == "example.com"

    def test_create_without_existing_check(self, mock_db_connection):
        """Тест создания без проверки существования."""
        mock_conn, mock_cursor = mock_db_connection
        
        url_model = URL()
        mock_cursor.fetchone.side_effect = [
            {"id": 1},
            {"id": 1, "name": "example.com", "created_at": "2023-01-01"},
        ]
        
        result = url_model.create(
            {"name": "example.com"},
            check_existing_entity=False,
        )
        
        assert result["name"] == "example.com"
        assert "created_at" in result


class TestUrlCheckModel:
    """Тесты для модели UrlCheck."""

    def test_table_name(self):
        """Тест имени таблицы."""
        check_model = UrlCheck()
        assert check_model.table_name == "url_checks"

    def test_create_url_check(self, mock_db_connection):
        """Тест создания проверки URL."""
        mock_conn, mock_cursor = mock_db_connection
        
        check_model = UrlCheck()
        mock_cursor.fetchone.side_effect = [
            {"id": 1},
            {
                "id": 1,
                "url_id": 1,
                "status_code": 200,
                "h1": "Test",
                "title": "Test",
                "description": "Test",
            },
        ]
        
        result = check_model.create({
            "url_id": 1,
            "status_code": 200,
            "h1": "Test",
            "title": "Test",
            "description": "Test"
        })
        
        assert result["url_id"] == 1
        assert result["status_code"] == 200
        assert result["h1"] == "Test"

    def test_filter_url_checks_by_url_id(self, mock_db_connection):
        """Тест фильтрации проверок по URL ID."""
        mock_conn, mock_cursor = mock_db_connection
        
        check_model = UrlCheck()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "url_id": 1, "status_code": 200},
            {"id": 2, "url_id": 1, "status_code": 201}
        ]
        
        result = check_model.filter({"url_id": 1})
        
        assert mock_cursor.fetchall.called
        assert len(result) == 2
        assert all(item["url_id"] == 1 for item in result)
