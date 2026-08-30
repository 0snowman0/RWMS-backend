from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import (
    IGenericRepository,
)
from Core.Domain.Models.user import User


class IUserRepository(
    IGenericRepository[User],
    Protocol,
):
    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        ...