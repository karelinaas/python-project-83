from bs4 import BeautifulSoup


def extract_seo_tags(html_content: str) -> dict[str, str | None]:
    """
    Извлекает SEO-теги из HTML-контента.
    
    Args:
        html_content: HTML-контент страницы
        
    Returns:
        Словарь с содержимым SEO-тегов (h1, title, description)
    """
    soup = BeautifulSoup(html_content, "html.parser")

    tag_params = {
        "h1": ("h1", None, None),
        "title": ("title", None, None),
        "description": ("meta", {"name": "description"}, "content"),
    }

    result: dict[str, str | None] = {}

    for param_name, (
        tag_name,
        search_attrs,
        tag_attr_name,
    ) in tag_params.items():
        tag = soup.find(tag_name, attrs=search_attrs)
        content = None
        if tag:
            if tag_attr_name:
                content = tag.get(tag_attr_name, "").strip()
            else:
                content = tag.get_text().strip()
        result[param_name] = content

    return result
