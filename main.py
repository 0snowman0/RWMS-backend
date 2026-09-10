from fastapi import FastAPI
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
)

configure_rate_limiting(app)

configure_mediator(app)

setup_api(app) 