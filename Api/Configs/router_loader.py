import importlib
import pkgutil

from fastapi import FastAPI


CONTROLLERS_PACKAGE = "Api.Controllers"


def register_routers(app: FastAPI):
    controllers = importlib.import_module(CONTROLLERS_PACKAGE)

    for _, controller_name, _ in pkgutil.iter_modules(controllers.__path__):
        controller_package_name = (
            f"{CONTROLLERS_PACKAGE}.{controller_name}"
        )

        controller_package = importlib.import_module(
            controller_package_name
        )

        for _, version_name, _ in pkgutil.iter_modules(
            controller_package.__path__
        ):
            if version_name not in {"V1", "V2"}:
                continue

            version_package_name = (
                f"{controller_package_name}.{version_name}"
            )

            version_package = importlib.import_module(
                version_package_name
            )

            for _, module_name, _ in pkgutil.iter_modules(
                version_package.__path__
            ):
                module_full_name = (
                    f"{version_package_name}.{module_name}"
                )

                module = importlib.import_module(module_full_name)

                router = getattr(module, "router", None)

                if router is None:
                    continue

                app.include_router(
                    router,
                    prefix=f"/api/{version_name.lower()}",
                )

                print(
                    f"Registered: {module_full_name} "
                    f"-> /api/{version_name.lower()}"
                )