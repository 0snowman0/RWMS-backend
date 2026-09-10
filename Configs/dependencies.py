from Core.Application.Contracts.DataBases.DatabaseRoutines.database_routine_executor import IDatabaseRoutineExecutor
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import IUnitOfWork
from Core.Application.Contracts.DependencyInjections.service_resolver import IServiceResolver
from Core.Application.Contracts.Identities.identity import ITokenService
from Core.Application.Contracts.Mapper.mapper import IMapper
from Core.Application.Contracts.Mediators.mediator import IMediator
from Core.Application.Mapping.mapping_configuration import configure_mapper
from Core.Application.Mediators.behavior_policy_resolver import BehaviorPolicyResolver
from Infrastructure.DependencyInjections.service_resolver import ServiceResolver
from Infrastructure.Identity.Services.Identities.identity import JWTTokenService

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Infrastructure.Mediators.behavior_factory import BehaviorFactory
from Infrastructure.Mediators.handler_factory import HandlerFactory
from Infrastructure.Mediators.mediator import Mediator
from Infrastructure.Persistence.Configs.PGdatabase import get_db
from Infrastructure.Persistence.DatabaseRoutines.postgres_routine_executor import PostgresRoutineExecutor
from Infrastructure.Persistence.UnitOfWorks.unit_of_works import SqlAlchemyUnitOfWork

# هر دپندنسی که اینجا اضافه میشه در get_service_resolver هم اضافه بشه 
# برای اینکه بعدا بتونه ازش در  هندلر های مدیت آر استفاده بکنه 
#-------------------------------------------

def get_token_service() -> ITokenService:
    return JWTTokenService()

TokenServiceDependency = Annotated[
    ITokenService,
    Depends(get_token_service)
]

#-------------------------------------------

def get_unit_of_work(
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session)

UOWDependency = Annotated[
        IUnitOfWork,
        Depends(get_unit_of_work),
]

#-------------------------------------------

_mapper = configure_mapper()

def get_mapper() -> IMapper:
    return _mapper

MapperDependency = Annotated[
    IMapper,
    Depends(get_mapper),
]

#-------------------------------------------

def get_database_routine_executor(
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    mapper: MapperDependency,
) -> IDatabaseRoutineExecutor:

    return PostgresRoutineExecutor(
        session=session,
        mapper=mapper,
    )


DatabaseRoutineExecutorDependency = Annotated[
    IDatabaseRoutineExecutor,
    Depends(get_database_routine_executor),
]

#-------------------------------------------

def get_service_resolver(
    uow: UOWDependency,
    mapper: MapperDependency,
    token_service: TokenServiceDependency,
    routine_executor: DatabaseRoutineExecutorDependency,
) -> IServiceResolver:

    resolver = ServiceResolver()

    resolver.add(
        IUnitOfWork,
        uow,
    )

    resolver.add(
        IMapper,
        mapper,
    )

    resolver.add(
        ITokenService,
        token_service,
    )
    
    resolver.add(
        IDatabaseRoutineExecutor,
        routine_executor,
    )
    
    return resolver


ServiceResolverDependency = Annotated[
    IServiceResolver,
    Depends(get_service_resolver),
]

#-------------------------------------------

def get_mediator(
    request: Request,
    service_resolver: ServiceResolverDependency,
) -> IMediator:

    handler_registry = (
        request.app.state.mediator_handler_registry
    )

    behavior_registry = (
        request.app.state.mediator_behavior_registry
    )

    handler_factory = HandlerFactory(
        service_resolver=service_resolver,
    )

    behavior_factory = BehaviorFactory(
        service_resolver=service_resolver,
    )

    behavior_policy_resolver = (
        BehaviorPolicyResolver()
    )

    return Mediator(
        handler_registry=handler_registry,
        handler_factory=handler_factory,
        behavior_registry=behavior_registry,
        behavior_factory=behavior_factory,
        behavior_policy_resolver=(
            behavior_policy_resolver
        ),
    )
    
MediatorDependency = Annotated[
    IMediator,
    Depends(get_mediator),
]    

#-------------------------------------------