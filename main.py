from fastapi import FastAPI
from Configs.RateLimiting.setup import configure_rate_limiting
from Configs.api_config import setup_api

app = FastAPI(
    title="RWMS Backend",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  
)

configure_rate_limiting(app)
setup_api(app) 