from typing import Any

from psycopg.rows import Row

from page_analyzer.models.base import UniqueModel


class URL(UniqueModel):
    table_name = "urls"

    def check_exists_before_insert(
        self,
        column_values: dict[str, Any],
    ) -> Row | None:
        if "name" not in column_values:
            raise Exception("Model is unique by name")

        return self._execute(
            query=f"SELECT * FROM {self.table_name} WHERE name = %s",
            params=(column_values["name"],),
            return_one_entity=True,
        )
