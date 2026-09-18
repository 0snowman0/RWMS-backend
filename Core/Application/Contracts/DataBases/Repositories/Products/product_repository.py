from typing import Protocol


from Core.Application.Contracts.DataBases.Repositories.Generics.repository import IGenericRepository
from Core.Domain.Models.Products.product import (
    Product,
)


class IProductRepository(
    IGenericRepository[Product],
    Protocol,
):
    pass