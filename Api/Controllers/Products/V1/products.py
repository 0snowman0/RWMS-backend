from fastapi import APIRouter

router = APIRouter(
    tags=["Products"]
)

@router.get("/products")
def get_products():
    return {"version": "v1", "message": "Products API"}


@router.get("/products/{product_id}")
def get_product(product_id: int):
    return {
        "version": "v1",
        "product_id": product_id,
    }