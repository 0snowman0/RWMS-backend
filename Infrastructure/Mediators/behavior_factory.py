import inspect

from Core.Application.Contracts.DependencyInjections.service_resolver import IServiceResolver
from Core.Application.Contracts.Mediators.behavior_factory import IBehaviorFactory
from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior


class BehaviorFactory(IBehaviorFactory):

    def __init__(
        self,
        service_resolver: IServiceResolver,
    ):
        self._service_resolver = service_resolver

    def create(
        self,
        behavior_class: type[IPipelineBehavior],
    ) -> IPipelineBehavior:

        constructor = inspect.signature(
            behavior_class.__init__
        )

        dependencies = {}

        for name, parameter in constructor.parameters.items():

            if name == "self":
                continue
            
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            
            dependency_type = parameter.annotation

            if dependency_type is inspect.Parameter.empty:
                raise TypeError(
                    f"Dependency '{name}' in "
                    f"'{behavior_class.__name__}' "
                    f"must have a type annotation."
                )

            dependencies[name] = (
                self._service_resolver.resolve(
                    dependency_type
                )
            )

        return behavior_class(
            **dependencies
        )