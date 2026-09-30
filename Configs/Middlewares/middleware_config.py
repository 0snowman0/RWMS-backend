from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Api.Middelwars.logging_context_middleware import LoggingContextMiddleware



def configure_middlewares(
    app: FastAPI,
) -> None:

    app.add_middleware(
        LoggingContextMiddleware
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    
    # Middleware بعدی
    # app.add_middleware(...)