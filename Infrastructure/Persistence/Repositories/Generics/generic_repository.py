from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
    Predicate,
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