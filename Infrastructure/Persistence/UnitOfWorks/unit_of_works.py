from sqlalchemy.ext.asyncio import AsyncSession

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.DataBases.Repositories.Users.user_repository import (
    IUserRepository,
)

from Infrastructure.Persistence.Repositories.Users.user_repository import (
    UserRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._users = UserRepository(
            session=session,
        )

    @property
    def users(self) -> IUserRepository:
        return self._users

    async def save_changes(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()