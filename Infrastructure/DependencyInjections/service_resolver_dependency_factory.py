import inspect
from typing import Any

from fastapi import Depends

from Core.Application.Contracts.DependencyInjections.service_resolver import (
    IServiceResolver,
)

from Infrastructure.DependencyInjections.mediator_service_registry import (
    MediatorServiceRegistry,
)

from Infrastructure.DependencyInjections.service_resolver import (
    ServiceResolver,
)


def build_service_resolver_dependency(
    registry: MediatorServiceRegistry,
):

    registrations = registry.get_all()

    async def get_service_resolver(
        **resolved_services: Any,
    ) -> IServiceResolver:

        resolver = ServiceResolver()

        for index, registration in enumerate(
            registrations
        ):

            service = resolved_services[
                f"service_{index}"
            ]

            resolver.add(
                registration.service_type,
                service,
            )

        return resolver

    # =========================================================
    # Dynamic FastAPI Dependency Signature
    # =========================================================

    parameters: list[
        inspect.Parameter
    ] = []

    for index, registration in enumerate(
        registrations
    ):

        parameters.append(
            inspect.Parameter(
                name=f"service_{index}",
                kind=(
                    inspect.Parameter.KEYWORD_ONLY
                ),
                annotation=(
                    registration.service_type
                ),
                default=Depends(
                    registration.provider
                ),
            )
        )

    get_service_resolver.__signature__ = (
        inspect.Signature(
            parameters=parameters,
            return_annotation=IServiceResolver,
        )
    )

    return get_service_resolver