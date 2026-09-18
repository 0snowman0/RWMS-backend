from Core.Application.Contracts.DataBases.Repositories.Products.product_repository import (
    IProductRepository,
)

from Core.Domain.Models.Products.product import (
    Product,
)

from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class ProductRepository(
    GenericRepository[Product],
    IProductRepository,
):

    def __init__(
        self,
        session,
    ) -> None:

        super().__init__(
            session=session,
            entity_type=Product,
        )