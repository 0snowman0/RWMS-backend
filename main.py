from fastapi import FastAPI
from Configs.api_config import setup_api

app = FastAPI(
    title="RWMS Backend",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  
)

setup_api(app) 