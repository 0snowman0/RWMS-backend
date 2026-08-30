from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Users.user_repository import (
    IUserRepository,
)


class IUnitOfWork(Protocol):

    @property
    def users(self) -> IUserRepository:
        ...

    async def save_changes(self) -> None:
        ...

    async def rollback(self) -> None:
        ...