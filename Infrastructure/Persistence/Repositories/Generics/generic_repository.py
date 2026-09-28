from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
    Predicate,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedRequestDto,
    PagedResultDto,
)


TEntity = TypeVar("TEntity")


class GenericRepository(
    IGenericRepository[TEntity],
    Generic[TEntity],
):
    def __init__(
        self,
        session: AsyncSession,
        entity_type: type[TEntity],
    ) -> None:
        self._session = session
        self._entity_type = entity_type

    def _resolve_sort_clause(
        self,
        sort_by: str | None = None,
        is_ascending: bool = True,
    ) -> Any:
        mapper = inspect(self._entity_type)
        col_attr = None

        if sort_by and sort_by.strip():
            # Case-insensitive lookup against column attributes
            lookup = {
                key.lower(): getattr(self._entity_type, key)
                for key in mapper.column_attrs.keys()
            }
            col_attr = lookup.get(sort_by.strip().lower())

        # Fallback to Primary Key if column not found or not provided
        if col_attr is None:
            pk_cols = mapper.primary_key
            if pk_cols:
                col_attr = getattr(self._entity_type, pk_cols[0].key)

        if col_attr is not None:
            return col_attr.asc() if is_ascending else col_attr.desc()

        return None

    async def get(
        self,
        predicate: Predicate,
    ) -> TEntity | None:
        statement = (
            select(self._entity_type)
            .where(predicate)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        predicate: Predicate | None = None,
    ) -> list[TEntity]:
        statement = select(self._entity_type)

        if predicate is not None:
            statement = statement.where(predicate)

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_paged(
        self,
        page_number: int = 1,
        page_size: int = 10,
        sort_by: str | None = None,
        is_ascending: bool = True,
        predicate: Predicate | None = None,
        pagination_params: PagedRequestDto[Any] | None = None,
    ) -> PagedResultDto[TEntity]:
        if pagination_params is not None:
            page_number = pagination_params.page_number
            page_size = pagination_params.page_size
            sort_by = pagination_params.sort_by
            is_ascending = pagination_params.is_ascending

        is_all = (page_number == -1 and page_size == -1)

        if not is_all:
            page_number = max(1, page_number)
            page_size = max(1, page_size)

        # 1. Total count query
        count_statement = select(func.count()).select_from(self._entity_type)
        if predicate is not None:
            count_statement = count_statement.where(predicate)

        total_count = await self._session.scalar(count_statement) or 0

        # 2. Items query with dynamic sorting and optional pagination
        statement = select(self._entity_type)

        if predicate is not None:
            statement = statement.where(predicate)

        sort_clause = self._resolve_sort_clause(
            sort_by=sort_by,
            is_ascending=is_ascending,
        )
        if sort_clause is not None:
            statement = statement.order_by(sort_clause)

        if not is_all:
            offset = (page_number - 1) * page_size
            statement = statement.offset(offset).limit(page_size)

        result = await self._session.execute(statement)
        items = list(result.scalars().all())

        return PagedResultDto[TEntity].create(
            items=items,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )

    async def add(
        self,
        entity: TEntity,
    ) -> TEntity:
        self._session.add(entity)

        return entity

    async def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        self._session.add(entity)

        return entity

    async def delete(
        self,
        entity: TEntity,
    ) -> None:
        await self._session.delete(entity)