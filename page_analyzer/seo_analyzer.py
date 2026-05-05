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
    
    # Извлечение h1
    h1_tag = soup.find("h1")
    h1_content = h1_tag.get_text().strip() if h1_tag else None
    
    # Извлечение title
    title_tag = soup.find("title")
    title_content = title_tag.get_text().strip() if title_tag else None
    
    # Извлечение meta description
    meta_description = soup.find("meta", attrs={"name": "description"})
    description_content = (
        meta_description.get("content", '').strip()
        if meta_description else None
    )
    
    return {
        "h1": h1_content,
        "title": title_content,
        "description": description_content
    }
