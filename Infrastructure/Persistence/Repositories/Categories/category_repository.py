from Core.Application.Contracts.DataBases.Repositories.Categories.category_repository import (
    ICategoryRepository,
)

from Core.Domain.Models.Categories.category import (
    Category,
)

from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class CategoryRepository(
    GenericRepository[Category],
    ICategoryRepository,
):

    def __init__(
        self,
        session,
    ) -> None:

        super().__init__(
            session=session,
            entity_type=Category,
        )

    async def get_by_name(
        self,
        name: str,
    ) -> Category | None:

        return await self.get(
            Category.name == name
        )