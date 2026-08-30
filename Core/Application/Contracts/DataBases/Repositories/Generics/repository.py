from typing import Generic, Protocol, TypeVar

from sqlalchemy.sql.elements import ColumnElement


TEntity = TypeVar("TEntity")

Predicate = ColumnElement[bool]


class IGenericRepository(Protocol, Generic[TEntity]):

    async def get(
        self,
        predicate: Predicate,
    ) -> TEntity | None:
        ...

    async def get_all(
        self,
        predicate: Predicate | None = None,
    ) -> list[TEntity]:
        ...

    async def add(
        self,
        entity: TEntity,
    ) -> TEntity:
        ...

    async def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        ...

    async def delete(
        self,
        entity: TEntity,
    ) -> None:
        ...