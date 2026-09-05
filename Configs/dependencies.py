from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import IUnitOfWork
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.Contracts.Mapper.mapper import IMapper
from Core.Application.Mapping.mapping_configuration import configure_mapper
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



_mapper = configure_mapper()

def get_mapper() -> IMapper:
    return _mapper

MapperDependency = Annotated[
    IMapper,
    Depends(get_mapper),
]