from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import IUnitOfWork
from Core.Application.Contracts.Identities.identity import ITokenService
from Infrastructure.Identity.Services.Identities.identity import JWTTokenService

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Infrastructure.Persistence.Configs.PGdatabase import get_db
from Infrastructure.Persistence.UnitOfWorks.unit_of_works import SqlAlchemyUnitOfWork



def get_token_service() -> ITokenService:
    return JWTTokenService()


def get_unit_of_work(
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session)