from Core.Application.Contracts.DataBases.Repositories.Users.user_repository import (
    IUserRepository,
)
from Core.Domain.Models.user import User

from Infrastructure.Persistence.Repositories.Generics.generic_repository import (
    GenericRepository,
)


class UserRepository(
    GenericRepository[User],
    IUserRepository,
):
    def __init__(
        self,
        session,
    ) -> None:
        super().__init__(
            session=session,
            entity_type=User,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return await self.get(
            User.email == email
        )