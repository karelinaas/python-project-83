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

        pattern = column_values["name"] + "%"
        return self._execute(
            query=(
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE %s"
            ),
            params=(pattern,),
            return_one_entity=True,
        )
