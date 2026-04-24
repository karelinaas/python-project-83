import abc
from typing import Any

from psycopg.rows import Row

from page_analyzer.config.database import get_db_connection


class BaseModel(abc.ABC):
    @property
    @abc.abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    def filter(
        self,
        filter_parameters: dict[str, Any],
        return_one_entity: bool = False,
    ) -> list[Row] | Row | None:
        filter_string = ""
        filter_values = tuple()

        for key, value in filter_parameters.items():
            filter_string += f"{key} = %s AND "
            filter_values += (value,)
        filter_string = filter_string.rstrip(" AND ")

        return self._execute(
            query=f"SELECT * FROM {self.table_name} WHERE {filter_string}",
            params=filter_values,
            return_one_entity=return_one_entity,
        )

    def get(self, value: Any, column: str = "id") -> Row | None:
        return self.filter({column: value}, return_one_entity=True)

    def create(
        self,
        column_values: dict[str, Any],
        *_,
        **__,
    ) -> Row | None:
        columns = ", ".join(column_values.keys())

        entity_id = self._execute(
            query=(
                f"INSERT INTO {self.table_name} ({columns}) "
                "VALUES (%s) RETURNING id"
            ),
            params=tuple(column_values.values()),
        )["id"]

        return self.get(entity_id)

    def get_all(
        self,
        *,
        order_by: tuple[str] | None = None,
        order_asc: bool = True,
    ) -> list[Row] | None:
        order_by_string = ""
        if order_by:
            order_by_string = " ORDER BY "
            order_by_string += ", ".join(order_by)
            if not order_asc:
                order_by_string += " DESC"
        return self._execute(
            query=f"SELECT * FROM {self.table_name}{order_by_string}",
            return_one_entity=False,
        )

    def _execute(
        self,
        *,
        query: str,
        params: tuple = tuple(),
        return_one_entity: bool = True,
    ) -> list[Row] | Row | None:
        """Единая точка входа для выполнения запросов."""
        with get_db_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(query, params)

                    if query.strip().upper().startswith(
                        ("INSERT", "UPDATE", "DELETE")
                    ):
                        conn.commit()

                    if return_one_entity:
                        return cur.fetchone()
                    return cur.fetchall()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()


class UniqueModel(BaseModel):
    table_name: str

    @abc.abstractmethod
    def check_exists_before_insert(self, *args, **kwargs) -> Row | None:
        raise NotImplementedError

    def create(
        self,
        column_values: dict[str, Any],
        check_existing_entity: bool = True,
        *args,
        **kwargs,
    ) -> Row | None:
        if check_existing_entity:
            existing_entity = self.check_exists_before_insert(column_values)
            if existing_entity:
                return existing_entity
        return super().create(column_values)
