import importlib
import pkgutil

import Core.Domain.Models


def import_all_models() -> None:
    package = Core.Domain.Models

    for module_info in pkgutil.walk_packages(
        package.__path__,
        prefix=f"{package.__name__}.",
    ):
        importlib.import_module(module_info.name)