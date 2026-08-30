import importlib
import pkgutil
from fastapi import FastAPI

CONTROLLERS_PACKAGE = "Api.Controllers"


def register_routers(app: FastAPI):
    
    def scan_package(package_name: str, prefix: str = ""):
        package = importlib.import_module(package_name)
        
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_name}.{module_name}"
            
            if is_pkg:
                new_prefix = f"{prefix}/{module_name}" if prefix else module_name
                scan_package(full_name, new_prefix)
            else:
                module = importlib.import_module(full_name)
                router = getattr(module, "router", None)
                
                if router is None:
                    continue
                
                version = "v1"
                path_parts = prefix.split("/")
                for part in path_parts:
                    if part.lower().startswith("v") and part[1:].isdigit():
                        version = part.lower()
                        break
                
                final_prefix = f"/api/{version}{prefix}"
                
                app.include_router(router, prefix=final_prefix)
    
    scan_package(CONTROLLERS_PACKAGE)