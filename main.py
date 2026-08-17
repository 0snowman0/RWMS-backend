from fastapi import FastAPI

from Api.Configs.router_loader import register_routers


app = FastAPI(
    title="RWMS Backend",
)


register_routers(app)