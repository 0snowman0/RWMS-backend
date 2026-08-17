from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def create_versioned_openapi(app: FastAPI, version: str):
    """تولید OpenAPI schema برای یک نسخه خاص"""
    prefix = f"/api/{version}"
    
    full_openapi = app.openapi()
    
    filtered_paths = {}
    for path, path_item in full_openapi.get("paths", {}).items():
        if path.startswith(prefix):
            filtered_paths[path] = path_item
    
    return {
        "openapi": full_openapi.get("openapi", "3.0.0"),
        "info": {
            "title": "RWMS Backend",
            "version": version.upper(),
            "description": f"RWMS API - {version.upper()}",
        },
        "paths": filtered_paths,
        "components": full_openapi.get("components", {}),
        "tags": full_openapi.get("tags", []),
    }