from psycopg.rows import Row

from page_analyzer.models.base import UniqueModel


class URL(UniqueModel):
    table_name = "urls"

    def check_exists_before_insert(self, url: str) -> Row | None:
        return self._execute(
            query=f"SELECT * FROM {self.table_name} WHERE name = %s",
            params=(url,),
            return_one_entity=True,
        )
