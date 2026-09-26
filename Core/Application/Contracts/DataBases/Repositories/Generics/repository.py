from typing import Any, Generic, Protocol, TypeVar

from sqlalchemy.sql.elements import ColumnElement

from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
    PagedResultDto,
)


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

    async def get_paged(
        self,
        page_number: int = 1,
        page_size: int = 10,
        sort_by: str | None = None,
        is_ascending: bool = True,
        predicate: Predicate | None = None,
        pagination_params: PagedRequestDto[Any] | None = None,
    ) -> PagedResultDto[TEntity]:
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