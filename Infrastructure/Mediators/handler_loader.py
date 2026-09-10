import importlib
import inspect
import pkgutil

from Core.Application.Contracts.Mediators.handler_loader import IHandlerLoader
from Core.Application.Contracts.Mediators.handler_registry import IHandlerRegistry
from Core.Application.Mediators.handler_decorators import HANDLER_REQUEST_ATTRIBUTE



class HandlerLoader(IHandlerLoader):

    def __init__(
        self,
        registry: IHandlerRegistry,
    ):
        self._registry = registry

    def load(
        self,
        package_name: str,
    ) -> None:

        package = importlib.import_module(
            package_name
        )

        # خود package
        self._register_from_module(
            package
        )

        # زیرماژول‌ها
        if hasattr(package, "__path__"):

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

            # فقط کلاس‌هایی که واقعاً
            # در همین module تعریف شده‌اند
            if obj.__module__ != module.__name__:
                continue

            request_type = getattr(
                obj,
                HANDLER_REQUEST_ATTRIBUTE,
                None,
            )

            if request_type is None:
                continue

            self._registry.register(
                request_type=request_type,
                handler_type=obj,
            )