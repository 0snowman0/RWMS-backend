from typing import Protocol

from Core.Application.Contracts.DataBases.Repositories.Categories.category_repository import (
 ICategoryRepository   
)
 
from Core.Application.Contracts.DataBases.Repositories.Products.product_repository import IProductRepository
from Core.Application.Contracts.DataBases.Repositories.Users.user_repository import (
    IUserRepository,
)


class IUnitOfWork(Protocol):

    @property
    def users(self) -> IUserRepository:
        ...

    @property
    def categories(self) -> ICategoryRepository:
        ...
    
    @property
    def products(
        self,
    ) -> IProductRepository:
        ...
    
    async def __aenter__(self) -> "IUnitOfWork":
        ...

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        ...

    async def save_changes(self) -> None:
        ...

    async def rollback(self) -> None:
        ...