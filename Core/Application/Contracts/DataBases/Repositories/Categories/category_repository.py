from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Generics.repository import IGenericRepository
from Core.Domain.Models.Categories.category import (
    Category,
)


class ICategoryRepository(
    IGenericRepository[Category],
    Protocol,
):

    async def get_by_name(
        self,
        name: str,
    ) -> Category | None:
        ...