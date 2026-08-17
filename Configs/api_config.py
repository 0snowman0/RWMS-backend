from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from Api.Configs.router_loader import register_routers
from Api.Configs.openapi import create_versioned_openapi


def setup_api(app: FastAPI):
    """تنظیمات کامل API"""
    
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    register_routers(app)
    
    @app.get("/openapi/{version}.json", include_in_schema=False)
    def get_openapi(version: str):
        if version not in {"v1", "v2"}:
            return JSONResponse(
                status_code=404,
                content={"message": "API version not found"}
            )
        
        openapi_schema = create_versioned_openapi(app, version)
        return JSONResponse(content=openapi_schema)
    
    @app.get("/docs", include_in_schema=False)
    def custom_swagger_ui():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RWMS API Docs</title>
            <link rel="stylesheet" href="/static/swagger-ui/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            
            <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
            <script src="/static/swagger-ui/swagger-ui-standalone-preset.js"></script>
            
            <script>
                window.onload = function() {
                    SwaggerUIBundle({
                        urls: [
                            { url: "/openapi/v1.json", name: "RWMS API V1" },
                            { url: "/openapi/v2.json", name: "RWMS API V2" }
                        ],
                        "urls.primaryName": "RWMS API V1",
                        dom_id: "#swagger-ui",
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        layout: "StandaloneLayout",
                        deepLinking: true
                    });
                };
            </script>
        </body>
        </html>
        """)