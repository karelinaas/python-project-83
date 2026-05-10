from page_analyzer.utils.seo_analyzer import extract_seo_tags


class TestSeoAnalyzer:
    """Тесты для модуля SEO анализатора."""

    def test_extract_seo_tags_complete(self, sample_html_content):
        """Тест извлечения всех SEO тегов из полного HTML."""
        result = extract_seo_tags(sample_html_content)
        
        assert result["title"] == "Test Page Title"
        assert result["description"] == "Test page description"
        assert result["h1"] == "Test H1 Header"

    def test_extract_seo_tags_missing_tags(self, sample_html_without_seo):
        """Тест обработки HTML без SEO тегов."""
        result = extract_seo_tags(sample_html_without_seo)
        
        assert result["title"] is None
        assert result["description"] is None
        assert result["h1"] is None

    def test_extract_seo_tags_partial_content(self):
        """Тест HTML с частичным содержимым SEO тегов."""
        html = """
        <html>
        <head>
            <title>Only Title</title>
        </head>
        <body>
            <h1>Only H1</h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Only Title"
        assert result["h1"] == "Only H1"
        assert result["description"] is None

    def test_extract_seo_tags_empty_description(self):
        """Тест обработки пустого мета-тега description."""
        html = """
        <html>
        <head>
            <title>Test</title>
            <meta name="description" content="">
        </head>
        <body>
            <h1>Test</h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Test"
        assert result["h1"] == "Test"
        assert result["description"] == ""

    def test_extract_seo_tags_whitespace_handling(self):
        """Тест обработки пробелов в содержимом тегов."""
        html = """
        <html>
        <head>
            <title>
                Title with spaces   
            </title>
            <meta name="description" content="  Description with spaces  ">
        </head>
        <body>
            <h1>
                H1 with spaces   
            </h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Title with spaces"
        assert result["description"] == "Description with spaces"
        assert result["h1"] == "H1 with spaces"

    def test_extract_seo_tags_multiple_h1(self):
        """Тест обработки нескольких H1 тегов (должен взять первый)."""
        html = """
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1>First H1</h1>
            <h1>Second H1</h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Test"
        assert result["h1"] == "First H1"

    def test_extract_seo_tags_nested_content(self):
        """Тест обработки вложенных элементов в H1."""
        html = """
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1><span>Nested</span> Content</h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Test"
        assert result["h1"] == "Nested Content"

    def test_extract_seo_tags_malformed_html(self):
        """Тест обработки некорректного HTML."""
        html = """
        <html>
        <head>
            <title>Test</title>
        <body>
            <h1>Missing closing tags
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Test"
        assert result["h1"] == "Missing closing tags"
        assert result["description"] is None

    def test_extract_seo_tags_empty_input(self):
        """Тест обработки пустой строки."""
        result = extract_seo_tags("")
        
        assert result["title"] is None
        assert result["description"] is None
        assert result["h1"] is None

    def test_extract_seo_tags_special_characters(self):
        """Тест обработки специальных символов в содержимом."""
        html = """
        <html>
        <head>
            <title>Тест &amp; Специальные символы</title>
            <meta 
                name="description" content="Описание с &quot;кавычками&quot;"
            >
        </head>
        <body>
            <h1>Заголовок с &lt;тегами&gt;</h1>
        </body>
        </html>
        """
        result = extract_seo_tags(html)
        
        assert result["title"] == "Тест & Специальные символы"
        assert result["description"] == 'Описание с "кавычками"'
        assert result["h1"] == "Заголовок с <тегами>"
