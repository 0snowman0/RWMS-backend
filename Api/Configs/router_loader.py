import importlib
import pkgutil

from fastapi import FastAPI


def register_routers(app: FastAPI):
    package_name = "Api.Controllers"

    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__,
        package.__name__ + ".",
    ):
        module = importlib.import_module(module_name)

        router = getattr(module, "router", None)

        if router is not None:
            app.include_router(router)
            print(f"Registered router: {module_name}")