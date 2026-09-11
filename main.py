from fastapi import FastAPI
from Configs.Lifespans.application_lifespan import application_lifespan
from Configs.Loggings.logging_config import configure_logging
from Configs.Middlewares.middleware_config import configure_middlewares
from Configs.RateLimiting.setup import configure_rate_limiting
from Configs.api_config import setup_api
from Configs.Mediators.setup import (
    configure_mediator,
)

app = FastAPI(
    title="RWMS Backend",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  
    lifespan=application_lifespan,
)

configure_logging(app)

configure_rate_limiting(app)

configure_mediator(app)

configure_middlewares(app)

setup_api(app) 