from fastapi import APIRouter

from Api.Configs.app_router import AppRouter
from Api.RateLimiting.decorators import rate_limit

router = AppRouter(
    tags=["Products"]
)

@router.get("/products")
@rate_limit("login")
def get_products():
    return {"version": "v1", "message": "Products API"}


@router.get("/products/{product_id}")
def get_product(product_id: int):
    return {
        "version": "v1",
        "product_id": product_id,
    }