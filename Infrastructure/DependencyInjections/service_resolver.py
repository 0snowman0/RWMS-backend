from typing import TypeVar

from Core.Application.Contracts.DependencyInjections.service_resolver import IServiceResolver



T = TypeVar("T")


class ServiceResolver(IServiceResolver):

    def __init__(self):
        self._services: dict[
            type,
            object,
        ] = {}

    def add(
        self,
        service_type: type[T],
        instance: T,
    ) -> None:

        self._services[
            service_type
        ] = instance

    def resolve(
        self,
        service_type: type[T],
    ) -> T:

        instance = self._services.get(
            service_type
        )

        if instance is None:
            raise KeyError(
                f"Service "
                f"'{service_type.__name__}' "
                f"was not registered."
            )

        return instance