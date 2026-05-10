from typing import Any

from page_analyzer.models.base import BaseModel


class UrlCheck(BaseModel):
    table_name = "url_checks"

    def get_list_with_urls(self, urls: list[dict[str, Any]]):
        url_ids_map = {str(url["id"]): dict(url) for url in urls}
        url_ids = ", ".join(url_ids_map.keys())

        query = f"""
            SELECT url_id, MAX(created_at) as last_check_date, status_code 
            FROM {self.table_name} 
            WHERE url_id in ({url_ids}) 
            GROUP BY url_id, status_code
        """

        urls_checks = self._execute(query=query, return_one_entity=False)

        for url_check in urls_checks:
            url_ids_map[str(url_check["url_id"])].update(url_check)

        return list(url_ids_map.values())
