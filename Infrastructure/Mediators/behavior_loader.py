import importlib
import inspect
import pkgutil

from Core.Application.Contracts.Mediators.behavior_loader import IBehaviorLoader
from Core.Application.Contracts.Mediators.behavior_registry import IBehaviorRegistry
from Core.Application.Mediators.behavior_decorators import BEHAVIOR_TYPE_ATTRIBUTE



class BehaviorLoader(IBehaviorLoader):

    def __init__(
        self,
        registry: IBehaviorRegistry,
    ):
        self._registry = registry

    def load(
        self,
        package_name: str,
    ) -> None:

        package = importlib.import_module(
            package_name
        )

        self._register_from_module(
            package
        )

        if hasattr(
            package,
            "__path__",
        ):

            for module_info in pkgutil.walk_packages(
                package.__path__,
                prefix=f"{package.__name__}.",
            ):

                module = importlib.import_module(
                    module_info.name
                )

                self._register_from_module(
                    module
                )

    def _register_from_module(
        self,
        module,
    ) -> None:

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass,
        ):

            if obj.__module__ != module.__name__:
                continue

            behavior_type = getattr(
                obj,
                BEHAVIOR_TYPE_ATTRIBUTE,
                None,
            )

            if behavior_type is None:
                continue

            self._registry.register(
                behavior_type=behavior_type,
                behavior_class=obj,
            )