import abc
from typing import Any

from psycopg.rows import Row

from page_analyzer.config.database import get_db_connection


class BaseModel(abc.ABC):
    @property
    @abc.abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    def check_exists_before_insert(self, *args, **kwargs) -> Row | None:
        raise NotImplementedError

    def filter(
        self,
        filter_parameters: dict[str, Any],
        return_one_entity: bool = True,
    ) -> list[Row] | Row | None:
        filter_string = ""
        filter_values = tuple()

        for key, value in filter_parameters.items():
            filter_string += f"{key} = %s AND "
            filter_values += (value,)
        filter_string = filter_string.rstrip(" AND ")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {self.table_name} WHERE {filter_string}",
                    filter_values,
                )
                if return_one_entity:
                    return cur.fetchone()
                return cur.fetchall()

    def get(self, filter_parameters: dict[str, Any]) -> Row | None:
        if len(filter_parameters) != 1:
            raise Exception("Method support only one filter parameter")
        return self.filter(filter_parameters, return_one_entity=True)

    def create(
        self,
        column_values: dict[str, Any],
        check_exists: bool = False,
    ) -> Row | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if check_exists:
                    existing_entity = self.check_exists_before_insert()
                    if existing_entity:
                        return existing_entity

                columns = ", ".join(column_values.keys())
                cur.execute(
                    (
                        f"INSERT INTO {self.table_name} ({columns}) "
                        "VALUES (%s) RETURNING id"
                    ),
                    tuple(column_values.values()),
                )
                entity_id = cur.fetchone()["id"]
                conn.commit()
                return self.get({"id": entity_id})

    def get_all(
        self,
        order_by: tuple[str] | None = None,
        order_asc: bool = True,
    ) -> list[Row] | None:
        order_by_string = ""
        if order_by:
            order_by_string = " ORDER BY "
            order_by_string += ", ".join(order_by)
            if not order_asc:
                order_by_string += " DESC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {self.table_name}{order_by_string}"
                )
                return cur.fetchall()
