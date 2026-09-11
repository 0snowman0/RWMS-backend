from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class MediatorServiceRegistration:

    service_type: type

    provider: Callable[..., Any]


class MediatorServiceRegistry:

    def __init__(
        self,
    ) -> None:

        self._services: dict[
            type,
            MediatorServiceRegistration,
        ] = {}

    # =========================================================
    # Register
    # =========================================================

    def register(
        self,
        service_type: type,
        provider: Callable[..., Any],
    ) -> None:

        if service_type in self._services:

            raise ValueError(
                f"Mediator service already registered: "
                f"{service_type.__name__}"
            )

        self._services[
            service_type
        ] = MediatorServiceRegistration(
            service_type=service_type,
            provider=provider,
        )

    # =========================================================
    # Get All
    # =========================================================

    def get_all(
        self,
    ) -> tuple[
        MediatorServiceRegistration,
        ...,
    ]:

        return tuple(
            self._services.values()
        )

    # =========================================================
    # Contains
    # =========================================================

    def contains(
        self,
        service_type: type,
    ) -> bool:

        return (
            service_type
            in self._services
        )


mediator_service_registry = (
    MediatorServiceRegistry()
)


def mediator_service(
    service_type: type,
):

    def decorator(
        provider: Callable[..., Any],
    ) -> Callable[..., Any]:

        mediator_service_registry.register(
            service_type=service_type,
            provider=provider,
        )

        return provider

    return decorator