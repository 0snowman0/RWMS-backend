from fastapi import FastAPI

from Api.Middelwars.logging_context_middleware import LoggingContextMiddleware



def configure_middlewares(
    app: FastAPI,
) -> None:

    app.add_middleware(
        LoggingContextMiddleware
    )
    
    
    # Middleware بعدی
    # app.add_middleware(...)